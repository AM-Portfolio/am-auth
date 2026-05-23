import os
import json
import requests
import sys
import argparse
import subprocess
import socket
import time
from pathlib import Path
from dotenv import load_dotenv

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
_ENV_FILE = _SCRIPT_DIR / ".env"
load_dotenv(_ENV_FILE, override=True)


def _resolve_kubeconfig(path: str) -> str:
    """Resolve VPS_KUBECONFIG relative to am-auth repo root."""
    raw = Path(path)
    if raw.is_absolute():
        return str(raw.resolve())
    for base in (_REPO_ROOT, _SCRIPT_DIR, _REPO_ROOT.parent):
        candidate = (base / raw).resolve()
        if candidate.is_file():
            return str(candidate)
    return str((_REPO_ROOT / raw).resolve())


class TunnelGuardian:
    """Manages the self-healing kubectl port-forward tunnel."""
    def __init__(self, port=8201, kubeconfig=None):
        self.port = port
        kube = kubeconfig or os.getenv("VPS_KUBECONFIG", "../VPS/kubeconfig.vps")
        self.kubeconfig = _resolve_kubeconfig(kube)
        self.process = None

    def is_port_open(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", self.port)) == 0

    def _kubectl_base(self):
        return ["kubectl", "--kubeconfig", self.kubeconfig]

    def verify_cluster(self) -> bool:
        if not Path(self.kubeconfig).is_file():
            print(f"[ERROR] Kubeconfig not found: {self.kubeconfig}")
            return False
        try:
            probe = subprocess.run(
                self._kubectl_base() + ["get", "svc", "-n", "vault", "vault-internal"],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except FileNotFoundError:
            print("[ERROR] kubectl not found on PATH")
            return False
        if probe.returncode != 0:
            print(f"[ERROR] Cannot reach cluster (kubeconfig={self.kubeconfig})")
            print(probe.stderr.strip() or probe.stdout.strip())
            return False
        print(f"[OK] Cluster reachable; vault-internal service found")
        return True

    def start(self):
        if self.is_port_open():
            print(f"[OK] Vault already reachable on 127.0.0.1:{self.port}")
            return True

        if not self.verify_cluster():
            return False

        print(
            f"[*] [TUNNEL] port-forward vault-internal:8200 -> 127.0.0.1:{self.port} "
            f"(kubeconfig={self.kubeconfig})"
        )
        cmd = self._kubectl_base() + [
            "port-forward",
            "-n",
            "vault",
            "svc/vault-internal",
            f"{self.port}:8200",
        ]
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        for _ in range(20):
            if self.is_port_open():
                print("[*] [TUNNEL] Vault tunnel established.")
                return True
            if self.process.poll() is not None:
                err = (self.process.stderr.read() or b"").decode(errors="replace").strip()
                print(f"[ERROR] port-forward exited: {err}")
                return False
            time.sleep(1)

        err = ""
        if self.process.stderr:
            err = self.process.stderr.read().decode(errors="replace").strip()
        print(f"[ERROR] Tunnel timed out (port {self.port} not open). {err}")
        return False

    def stop(self):
        if self.process:
            print(f"[*] [TUNNEL] Shutting down tunnel (PID {self.process.pid})...")
            self.process.terminate()
            self.process.wait()

class VaultOrchestrator:
    def __init__(self):
        self.addr = os.getenv("VAULT_ADDR", "http://localhost:8201").rstrip("/")
        self.token = os.getenv("VAULT_TOKEN")
        if not self.token:
            raise SystemExit(
                f"[ERROR] VAULT_TOKEN is not set. Copy scripts/.env.template to "
                f"scripts/.env and set your root token."
            )
        self.headers = {"X-Vault-Token": self.token, "Content-Type": "application/json"}
        self.guardian = TunnelGuardian(
            port=int(os.getenv("VAULT_TUNNEL_PORT", "8201")),
            kubeconfig=os.getenv("VPS_KUBECONFIG"),
        )

    def ensure_unsealed(self) -> bool:
        """Unseal Vault when sealed and VAULT_UNSEAL_KEY_B64 is configured."""
        try:
            resp = requests.get(f"{self.addr}/v1/sys/seal-status", timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"[ERROR] Cannot reach Vault at {self.addr}: {exc}")
            return False

        if not resp.json().get("sealed"):
            return True

        unseal_key = os.getenv("VAULT_UNSEAL_KEY_B64", "").strip()
        if not unseal_key:
            print("[ERROR] Vault is sealed. Set VAULT_UNSEAL_KEY_B64 in scripts/.env")
            return False

        print("[*] Vault is sealed — submitting unseal key...")
        unseal_resp = requests.post(
            f"{self.addr}/v1/sys/unseal",
            json={"key": unseal_key},
            timeout=15,
        )
        if unseal_resp.status_code != 200:
            print(f"[ERROR] Unseal failed: {unseal_resp.text}")
            return False

        if unseal_resp.json().get("sealed"):
            print("[ERROR] Vault still sealed after unseal (wrong key or more keys required).")
            return False

        print("[OK] Vault unsealed.")
        return True

    def backup(self, output_path=None):
        """Recursively backs up the KV-v2 mounts."""
        output_path = output_path or os.getenv(
            "VAULT_BACKUP_DIR",
            str(_SCRIPT_DIR.parent / "vault" / "backups"),
        )
        print("[*] Starting Recursive Vault Backup...")
        if not self.guardian.start():
            return
        if not self.ensure_unsealed():
            return
        
        # We target the core mounts you use
        mounts = ["kv", "secret", "apps"]
        all_data = {
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
            "vault_addr": self.addr,
            "data": {}
        }

        print(f"[INFO] Crawling mounts: {', '.join(mounts)}")
        
        for mount in mounts:
            print(f"[-] Crawling mount: {mount}/")
            paths = self._list_recursive(mount)
            print(f"   [OK] Found {len(paths)} secrets in {mount}/")
            for path in paths:
                data = self._read_kv_payload(path)
                if data:
                    all_data["data"][path] = data

        # Ensure directory exists
        os.makedirs(output_path, exist_ok=True)
        filename = f"vps_vault_full_backup_{all_data['timestamp']}.json"
        full_dest = os.path.join(output_path, filename)
        
        with open(full_dest, "w") as f:
            json.dump(all_data, f, indent=2)
            
        print(f"\n[SUCCESS] Full backup saved to: {os.path.abspath(full_dest)}")

    def _list_recursive(self, mount, path=""):
        """Recursively lists all keys in a KV-v2 mount using the metadata API."""
        full_metadata_path = f"{mount}/metadata/{path}".strip("/")
        api_url = f"{self.addr}/v1/{full_metadata_path}?list=true"
        
        resp = requests.get(api_url, headers=self.headers)
        if resp.status_code != 200:
            return []
            
        keys = resp.json().get("data", {}).get("keys", [])
        results = []
        
        for key in keys:
            if key.endswith("/"):
                # Recursive call for folders
                results.extend(self._list_recursive(mount, f"{path}{key}"))
            else:
                # Add file path
                results.append(f"{mount}/{path}{key}".replace("//", "/"))
        return results

    def _read_kv_payload(self, path):
        """Reads data from a specific KV-v2 path."""
        parts = path.split("/", 1)
        api_url = f"{self.addr}/v1/{parts[0]}/data/{parts[1]}"
        resp = requests.get(api_url, headers=self.headers)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("data")
        return None

    def sync(self, blueprint_path=None):
        """Deploys a blueprint to the apps/ engine."""
        blueprint_path = blueprint_path or os.getenv(
            "VAULT_BLUEPRINT_PATH",
            str(_SCRIPT_DIR.parent / "vault" / "blueprints" / "v3_master.json"),
        )
        print(f"[*] Loading Blueprint: {blueprint_path}")
        if not os.path.exists(blueprint_path):
            print(f"[ERROR] Blueprint not found at {blueprint_path}")
            return

        with open(blueprint_path, "r") as f:
            config = json.load(f)
        
        # Correctly parse the v3_master format
        blueprint = config.get("vault_architecture_v3_master", {}).get("blueprint", {})
        if not blueprint:
            print("[ERROR] Invalid blueprint format.")
            return

        if not self.guardian.start():
            return
        if not self.ensure_unsealed():
            return

        print("\n[*] Starting Master Synchronization...")
        for mount, envs in blueprint.items():
            for env, layers in envs.items():
                print(f"\n[-] Environment: {env.upper()}")
                for layer, services in layers.items():
                    for service, data in services.items():
                        path = f"{mount}/{env}/{layer}/{service}"
                        print(f" [+] Syncing: {path}")
                        self._write_kv2(path, data)
        print("\n[*] Synchronization Successful.")

    def _write_kv2(self, path, data):
        parts = path.split("/", 1)
        api_url = f"{self.addr}/v1/{parts[0]}/data/{parts[1]}"
        resp = requests.post(api_url, headers=self.headers, json={"data": data})
        if resp.status_code not in [200, 204]:
            print(f" [!] Error writing {path}: {resp.text}")

    def provision(self):
        """Administrative provisioning tasks."""
        if not self.guardian.start():
            return
        if not self.ensure_unsealed():
            return
        
        # 1. Secret Engines
        print("[*] Checking Infrastructure Mounts...")
        resp = requests.get(f"{self.addr}/v1/sys/mounts", headers=self.headers)
        if "apps/" not in resp.json():
            print("[*] Enabling 'apps/' secret engine...")
            requests.post(f"{self.addr}/v1/sys/mounts/apps", headers=self.headers, json={"type": "kv", "options": {"version": "2"}})
            print("[SUCCESS] 'apps/' engine enabled.")
        else:
            print("[OK] 'apps/' engine already exists.")

        # 2. Security Policies
        self.provision_policies()

    def provision_policies(self, policy_dir=None):
        """Enumerates and applies all HCL policies in the policy directory."""
        policy_dir = policy_dir or os.getenv(
            "VAULT_POLICY_DIR",
            str(_SCRIPT_DIR.parent / "vault" / "policies"),
        )
        print(f"[*] Provisioning security policies from {policy_dir}/...")
        if not os.path.exists(policy_dir):
            print(f"[WARN] Policy directory {policy_dir} not found.")
            return

        for policy_file in Path(policy_dir).glob("*.hcl"):
            policy_name = policy_file.stem
            print(f" [+] Applying policy: {policy_name}")
            with open(policy_file, "r") as f:
                rules = f.read()
            
            api_url = f"{self.addr}/v1/sys/policy/{policy_name}"
            resp = requests.post(api_url, headers=self.headers, json={"policy": rules})
            if resp.status_code not in [200, 204]:
                print(f"  [!] Error applying {policy_name}: {resp.text}")
            else:
                print(f"  [OK] Policy {policy_name} applied.")

    def close(self):
        self.guardian.stop()

def main():
    parser = argparse.ArgumentParser(description="ASRAX Vault Orchestrator")
    parser.add_argument("--backup", action="store_true", help="Backup Vault data")
    parser.add_argument("--sync", action="store_true", help="Sync data from blueprint")
    parser.add_argument("--provision", action="store_true", help="Provision mounts")
    
    args = parser.parse_args()
    orch = VaultOrchestrator()
    
    try:
        if args.provision: orch.provision()
        if args.sync: orch.sync()
        if args.backup: orch.backup()
    finally:
        orch.close()

if __name__ == "__main__":
    main()
