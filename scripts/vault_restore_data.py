import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://localhost:8201").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
BACKUP_FILE = "vault/backups/vps_vault_full_backup_20260422_000034.json"

def restore():
    if not os.path.exists(BACKUP_FILE):
        print(f"[ERROR] Backup file not found: {BACKUP_FILE}")
        return

    with open(BACKUP_FILE, "r") as f:
        backup_data = json.load(f)

    headers = {
        "X-Vault-Token": VAULT_TOKEN,
        "Content-Type": "application/json"
    }

    print(f"[*] Starting restoration to {VAULT_ADDR}...")
    
    data_map = backup_data.get("data", {})
    for path, payload in data_map.items():
        # Handle KV-v2 path structure: mount/data/rest/of/path
        parts = path.split("/", 1)
        if len(parts) < 2:
            print(f" [!] Skipping invalid path: {path}")
            continue
            
        mount = parts[0]
        secret_path = parts[1]
        
        # Construct the KV-v2 data write URL
        url = f"{VAULT_ADDR}/v1/{mount}/data/{secret_path}"
        
        print(f" [+] Restoring: {path}")
        resp = requests.post(url, headers=headers, json={"data": payload})
        
        if resp.status_code not in [200, 204]:
            print(f"  [!] Failed to restore {path}: {resp.status_code} - {resp.text}")
        else:
            print(f"  [OK] Restored {path}")

    print("\n[SUCCESS] Restoration complete.")

if __name__ == "__main__":
    restore()
