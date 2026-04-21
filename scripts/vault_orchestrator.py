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

load_dotenv()

class TunnelGuardian:
    """Manages the self-healing kubectl port-forward tunnel."""
    def __init__(self, port=8201, kubeconfig=None):
        self.port = port
        self.kubeconfig = kubeconfig or os.getenv("VPS_KUBECONFIG", "kubeconfig.vps")
        self.process = None

    def is_port_open(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", self.port)) == 0

    def start(self):
        if self.is_port_open():
            return True

        print(f"[*] [TUNNEL] Starting self-healing tunnel to VPS on port {self.port}...")
        env = os.environ.copy()
        env["KUBECONFIG"] = self.kubeconfig
        
        cmd = ["kubectl", "port-forward", "svc/vault-internal", f"{self.port}:8200", "-n", "vault"]
        self.process = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for port to become reachable
        for _ in range(10):
            if self.is_port_open():
                print("[*] [TUNNEL] Vault tunnel established.")
                return True
            time.sleep(1)
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
        self.headers = {"X-Vault-Token": self.token, "Content-Type": "application/json"}
        self.guardian = TunnelGuardian()

    def backup(self, output_path="vault/backups"):
        """Recursively backs up the KV-v2 mounts."""
        print("[*] Starting Recursive Vault Backup...")
        if not self.guardian.start(): return
        
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

    def sync(self, blueprint_path="vault/blueprints/v3_master.json"):
        """Deploys a blueprint to the apps/ engine."""
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

        if not self.guardian.start(): return
        
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
        if not self.guardian.start(): return
        print("[*] Checking Infrastructure Mounts...")
        resp = requests.get(f"{self.addr}/v1/sys/mounts", headers=self.headers)
        if "apps/" not in resp.json():
            print("[*] Enabling 'apps/' secret engine...")
            requests.post(f"{self.addr}/v1/sys/mounts/apps", headers=self.headers, json={"type": "kv", "options": {"version": "2"}})
            print("[SUCCESS] 'apps/' engine enabled.")
        else:
            print("[OK] 'apps/' engine already exists.")

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
