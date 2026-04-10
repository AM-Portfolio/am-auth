#!/usr/bin/env python3
"""
update_vault.py - Update HashiCorp Vault KV-v2 secrets with read-modify-write cycle.
Supports single key-value updates or bulk synchronization from a credentials file.
"""
import os
import sys
import argparse
import json
import urllib.request
import urllib.error
import re
from pathlib import Path

def get_vault_credentials(cred_file=None):
    """Read Vault credentials from provided file or fallback to am-infra/generated-credentials.txt"""
    # Prefer explicitly provided file (likely the centralized one)
    search_paths = [
        Path(cred_file) if cred_file else None,
        Path("../am-infra/infrastructure-secrets/latest/credentials.txt"),
        Path("../am-infra/generated-credentials.txt"),
    ]
    
    creds = {}
    for path in filter(None, search_paths):
        if path.exists():
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("VAULT_ROOT_TOKEN="):
                        creds["token"] = line.split("=", 1)[1]
                    elif line.startswith("VAULT_URL="):
                        creds["url"] = line.split("=", 1)[1]
            if creds.get("token") and creds.get("url"):
                break
                 
    return creds.get("token"), creds.get("url")

def parse_credentials_file(file_path):
    """
    Parses a credentials.txt file into a dictionary of categories.
    Format expected:
    # --- CATEGORY
    KEY=VALUE
    """
    data = {}
    current_category = "general"
    
    if not os.path.exists(file_path):
        print(f"[ERROR] Sync file not found at {file_path}")
        return None

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("# =="):
                continue
            
            # Match headers like # --- MONGODB
            header_match = re.match(r"^#\s*---\s*([A-Z0-9_\-]+)", line)
            if header_match:
                current_category = header_match.group(1).lower()
                if current_category not in data:
                    data[current_category] = {}
                continue
            
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                if current_category not in data:
                    data[current_category] = {}
                data[current_category][key.strip()] = value.strip()
                
    return data

def update_vault_path(url, headers, category, env, key, value=None, bulk_data=None):
    """Performs the read-modify-write cycle for a specific category path."""
    print(f"[INFO] Processing: am-auth/{env}/{category}")

    # 1. Read step to preserve existing keys (Read-Modify-Write)
    existing_data = {}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            existing_data = res_json.get("data", {}).get("data", {})
            print(f"   [OK] Found {len(existing_data)} existing keys.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("   [INFO] Path does not exist. Creating new.")
    except Exception as e:
        print(f"   [WARN] Read failed: {e}. Starting fresh.")

    # 2. Merge data
    if bulk_data:
        existing_data.update(bulk_data)
        print(f"   [NEW] Merging {len(bulk_data)} keys from file.")
    elif key and value is not None:
        existing_data[key] = value
        print(f"   [NEW] Updating key: {key}")

    payload = {"data": existing_data}

    # 3. Write back into Vault KVv2
    try:
        req_post = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode('utf-8'), method="POST")
        with urllib.request.urlopen(req_post) as response_post:
            if response_post.status in [200, 204]:
                print(f"   [SUCCESS] Path 'am-auth/{env}/{category}' is in sync.")
            else:
                print(f"   [ERROR] Writing: Status {response_post.status}")
                return False
    except Exception as e:
        print(f"   [ERROR] Failed: {e}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Update and merge secrets into HashiCorp Vault KV-v2")
    parser.add_argument("category", nargs="?", help="Secret category (e.g. database)")
    parser.add_argument("key", nargs="?", help="Key of the secret to update")
    parser.add_argument("value", nargs="?", help="Value of the secret to save")
    parser.add_argument("--sync-file", help="Path to credentials.txt for bulk sync")
    parser.add_argument("--env", default="preprod", help="Environment (default: preprod)")
    parser.add_argument("--vault-address", help="Override Vault Address")
    parser.add_argument("--vault-token", help="Override Vault Root Token")

    args = parser.parse_args()

    # 1. Resolve Vault Credentials
    token_file, url_file = get_vault_credentials(args.sync_file)
    vault_addr = args.vault_address or os.getenv("VAULT_ADDR") or url_file or "http://localhost:8200"
    vault_token = args.vault_token or os.getenv("VAULT_TOKEN") or token_file

    if not vault_token:
        print("[ERROR] No Vault Token found. Use VAULT_TOKEN env or ensure it exists in the sync file.")
        sys.exit(1)

    print(f"[INFO] Target Vault: {vault_addr}")
    headers = {"X-Vault-Token": vault_token, "Content-Type": "application/json"}

    # 2. Bulk Sync mode
    if args.sync_file:
        sync_data = parse_credentials_file(args.sync_file)
        if not sync_data:
            sys.exit(1)
        
        print(f"[INFO] Bulk Sync: Found {len(sync_data)} categories in {args.sync_file}")
        for category, bulk_kv in sync_data.items():
            url = f"{vault_addr}/v1/secret/data/am-auth/{args.env}/{category}"
            update_vault_path(url, headers, category, args.env, None, None, bulk_kv)
    
    # 3. Single Key mode
    elif args.category and args.key and args.value:
        url = f"{vault_addr}/v1/secret/data/am-auth/{args.env}/{args.category}"
        update_vault_path(url, headers, args.category, args.env, args.key, args.value)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
