#!/usr/bin/env python3
"""
update_vault.py - Update HashiCorp Vault KV-v2 secrets with read-modify-write cycle.
"""
import os
import sys
import argparse
import json
import urllib.request
import urllib.error
from pathlib import Path

def get_vault_credentials():
    """Read Vault credentials from am-infra/generated-credentials.txt"""
    cred_path = Path("/workspaces/am-repos/am-infra/generated-credentials.txt")
    creds = {}
    
    if not cred_path.exists():
         print(f"⚠️ Warning: Credentials file missing at {cred_path}")
         return None, None

    with open(cred_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("VAULT_ROOT_TOKEN="):
                creds["token"] = line.split("=", 1)[1]
            elif line.startswith("VAULT_URL="):
                 creds["url"] = line.split("=", 1)[1]
                 
    return creds.get("token"), creds.get("url")

def main():
    parser = argparse.ArgumentParser(description="Update and merge secrets into HashiCorp Vault KV-v2")
    parser.add_argument("category", help="Secret category/subpath (e.g. database, jwt, internal-jwt)")
    parser.add_argument("key", help="Key of the secret to add/update")
    parser.add_argument("value", help="Value of the secret to save")
    parser.add_argument("--env", default="local", help="Environment (default: local)")
    parser.add_argument("--vault-address", help="Override Vault Address")
    parser.add_argument("--vault-token", help="Override Vault Root Token")

    args = parser.parse_args()

    # 1. Resolve Vault Address and Token
    token_file, url_file = get_vault_credentials()
    vault_addr = args.vault_address or os.getenv("VAULT_ADDR") or url_file or "http://localhost:8080"
    vault_token = args.vault_token or os.getenv("VAULT_TOKEN") or token_file

    if not vault_token:
         print("❌ Error: Vault Token is required. Set VAULT_TOKEN env or provide --vault-token")
         sys.exit(1)

    print(f"🔗 Vault Address: {vault_addr}")
    # Prepare HTTP headers
    headers = {
        "X-Vault-Token": vault_token,
        "Content-Type": "application/json"
    }

    # 2. Build path (KVv2 stores data at /secret/data/...)
    # Layout matches values.yaml: secret/data/am-auth/{env}/{category}
    request_path = f"v1/secret/data/am-auth/{args.env}/{args.category}"
    url = f"{vault_addr}/{request_path}"
    
    print(f"📖 Fetching current keys at: am-auth/{args.env}/{args.category}")

    # 3. Read step to preserve existing keys (Read-Modify-Write)
    existing_data = {}
    try:
         req = urllib.request.Request(url, headers=headers)
         with urllib.request.urlopen(req) as response:
              res_json = json.loads(response.read().decode('utf-8'))
              existing_data = res_json.get("data", {}).get("data", {})
              print(f"✅ Found existing data with {len(existing_data)} keys.")
    except urllib.error.HTTPError as e:
          if e.code == 404:
               print("ℹ️ Path does not exist. Creating new secret structure.")
          else:
               print(f"⚠️ Warning: Reading path returned HTTP {e.code}. Proceeding with fresh data.")
    except Exception as e:
          print(f"⚠️ Read attempt failed: {e}. Defaulting to empty struct.")

    # 4. Update dictionary with new key-value item
    existing_data[args.key] = args.value
    payload = {
        "data": existing_data
    }

    # 5. Write back into Vault KVv2
    print(f"✍️ Writing merged payload back to Vault...")
    try:
         req_post = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode('utf-8'), method="POST")
         with urllib.request.urlopen(req_post) as response_post:
              if response_post.status in [200, 204]:
                   print(f"✅ Success! Updated key '{args.key}' in secret path 'am-auth/{args.env}/{args.category}'")
              else:
                   print(f"❌ Error writing to Vault: Status {response_post.status}")
                   sys.exit(1)
    except Exception as e:
         print(f"❌ Execution failed: {e}")
         sys.exit(1)

if __name__ == "__main__":
    main()
