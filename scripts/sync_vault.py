#!/usr/bin/env python3
"""
sync_vault.py - Advanced, modular Vault secret synchronization tool.
Designed for application-centric secret management with automated backups.
"""
import os
import sys
import argparse
import json
import requests
import re
import ssl
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class ANSI:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

class VaultProvider:
    """Handles low-level communication with HashiCorp Vault API."""
    def __init__(self, addr: str, token: str):
        self.addr = addr.rstrip("/")
        self.token = token
        self.headers = {
            "X-Vault-Token": token,
            "Content-Type": "application/json"
        }

    def lookup_self(self) -> bool:
        """Checks if the current token is valid."""
        url = f"{self.addr}/v1/auth/token/lookup-self"
        try:
            # Note: verify=False is used for local development with self-signed certs
            response = requests.get(url, headers=self.headers, verify=False, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"   {ANSI.RED}[DEBUG]{ANSI.RESET} Lookup self failed: {e}")
            return False

    def read(self, path: str) -> Optional[Dict[str, Any]]:
        """Reads a KV-v2 secret path."""
        api_path = path.replace("secret/", "secret/data/", 1)
        url = f"{self.addr}/v1/{api_path}"
        try:
            response = requests.get(url, headers=self.headers, verify=False, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", {}).get("data", {})
            elif response.status_code == 404:
                return None
            else:
                return None
        except Exception:
            return None

    def write(self, path: str, data: Dict[str, Any]) -> bool:
        """Writes a KV-v2 secret path."""
        api_path = path.replace("secret/", "secret/data/", 1)
        url = f"{self.addr}/v1/{api_path}"
        try:
            response = requests.post(url, headers=self.headers, json={"data": data}, verify=False, timeout=10)
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"{ANSI.RED}[ERROR]{ANSI.RESET} Write failed for {path}: {e}")
            return False

class CredentialParser:
    """Advanced regex-based parser for human-readable credentials.txt."""
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = ""
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.content = f.read()

    def get_vault_info(self) -> (Optional[str], Optional[str]):
        """Extracts Vault Token and URL."""
        token_match = re.search(r"Token.*?(hvs\.[a-zA-Z0-9]+)", self.content, re.IGNORECASE)
        url_match = re.search(r"Vault.*?(https?://[^\n\s]+)", self.content, re.IGNORECASE)
        token = token_match.group(1) if token_match else None
        url = url_match.group(1).rstrip("/") if url_match else None
        return token, url

    def clean_key(self, k: str) -> str:
        """Transforms human labels into standard Env Var names."""
        k = k.upper().replace("POSTGRESQL", "POSTGRES")
        k = k.replace("PASS", "PASSWORD")
        k = k.replace("USER", "USERNAME")
        k = k.replace("BOOTSTRAP", "BOOTSTRAP_SERVERS")
        # Clean special chars, replace spaces with underscores
        k = re.sub(r"[^\w\s\-]+", "", k)
        k = re.sub(r"[\s\-]+", "_", k)
        return k.strip("_")

    def extract_sections(self) -> Dict[str, Dict[str, str]]:
        """Extracts structured data using robust lookahead."""
        # Stop at any major emoji header or end of file
        stop_pattern = r"(?=\n[🔐📊📦🔑🚀🔒⚙️🔌]| \=\=\=\=|$)"
        
        sections = {
            "infra/identity": rf"🔐 AUTHENTIK IDENTITY HUB\n(.*?){stop_pattern}",
            "infra/management": rf"📊 INFRASTRUCTURE DASHBOARDS\n(.*?){stop_pattern}",
            "infra/storage": rf"📦 STORAGE & DATA STORES\n(.*?){stop_pattern}",
            "apps/database": rf"🔑 ROOT DATABASE PASSWORDS \(OS LEVEL\)\n(.*?){stop_pattern}",
            "apps/paas": rf"🚀 CLOUD DATABASE ACCESS \(EXTERNAL\)\n(.*?){stop_pattern}",
            "apps/security": rf"🔒 APPS SECURITY & TOKENS\n(.*?){stop_pattern}",
            "apps/config": rf"⚙️ APPS RUNTIME CONFIG\n(.*?){stop_pattern}",
            "apps/api": rf"🔌 THIRD-PARTY API KEYS\n(.*?){stop_pattern}"
        }
        
        extracted = {}
        for key, pattern in sections.items():
            match = re.search(pattern, self.content, re.DOTALL)
            if match:
                section_text = match.group(1)
                kv = {}
                for line in section_text.splitlines():
                    line = line.strip()
                    if ":" in line:
                        k, v = line.split(":", 1)
                        clean_k = self.clean_key(k)
                        kv[clean_k] = v.strip()
                    elif "=" in line:
                        k, v = line.split("=", 1)
                        clean_k = self.clean_key(k)
                        kv[clean_k] = v.strip()
                if kv:
                    extracted[key] = kv
        return extracted

class BackupManager:
    """Manages local snapshots of Vault data."""
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def save(self, category: str, data: Dict[str, Any]):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = category.replace("/", "_")
        filename = f"backup_{safe_name}_{timestamp}.json"
        path = self.backup_dir / filename
        with open(path, "w") as f:
            json.dump({"category": category, "timestamp": timestamp, "data": data}, f, indent=2)
        print(f"   {ANSI.BLUE}[BACKUP]{ANSI.RESET} Saved previous state to {path}")

def main():
    parser = argparse.ArgumentParser(description="Application-Centric Vault Sync Orchestrator")
    parser.add_argument("--file", default="../../am-infra/infrastructure-secrets/latest/credentials.txt", help="Source credentials file")
    parser.add_argument("--env", default="local", help="Target environment prefix (default: local)")
    parser.add_argument("--dry-run", action="store_true", help="Parse and show mapping without writing")
    parser.add_argument("--no-backup", action="store_true", help="Skip local backups")
    
    args = parser.parse_args()

    print(f"{ANSI.BOLD}Step 1: Parsing Source {args.file}...{ANSI.RESET}")
    if not os.path.exists(args.file):
        print(f"{ANSI.RED}[ERROR]{ANSI.RESET} Source file not found: {os.path.abspath(args.file)}")
        sys.exit(1)
        
    creds_parser = CredentialParser(args.file)
    token, url = creds_parser.get_vault_info()
    sections = creds_parser.extract_sections()

    if not url or not token:
        print(f"{ANSI.RED}[ERROR]{ANSI.RESET} No Vault Token/URL found in {args.file}")
        sys.exit(1)

    print(f"   [OK] Found Vault URL: {url}")
    print(f"   [OK] Found {len(sections)} sections for synchronization.")

    if args.dry_run:
        print(f"\n--- DRY RUN MODE ---")
        for path_suffix, data in sections.items():
            full_path = f"secret/{args.env}/{path_suffix}"
            print(f"[*] Would sync to: {ANSI.BOLD}{full_path}{ANSI.RESET}")
            for k, v in sorted(data.items()):
                k_safe = k.encode('ascii', 'ignore').decode('ascii')
                v_safe = v.encode('ascii', 'ignore').decode('ascii')
                print(f"   - {k_safe}: {v_safe[:5]}***{v_safe[-2:] if len(v_safe)>2 else ''}")
        return

    vault = VaultProvider(url, token)
    backup = BackupManager()

    print(f"\n{ANSI.BOLD}Step 2: Commencing Synchronization...{ANSI.RESET}")
    if not vault.lookup_self():
        print(f"   {ANSI.RED}[ERROR]{ANSI.RESET} Vault token is invalid or expired.")
        sys.exit(1)
    
    print(f"   {ANSI.GREEN}[OK]{ANSI.RESET} Vault token is valid.")

    for path_suffix, new_data in sections.items():
        full_path = f"secret/{args.env}/{path_suffix}"
        print(f"[-] Processing {ANSI.GREEN}{full_path}{ANSI.RESET}...")

        # A. Read current state for backup
        existing_data = vault.read(full_path)
        if existing_data and not args.no_backup:
            backup.save(path_suffix, existing_data)
        
        # B. Overwrite Vault (Ensures legacy duplicates are removed)
        # credentials.txt is the ONLY source of truth
        target_data = new_data
        
        if vault.write(full_path, target_data):
            print(f"   {ANSI.GREEN}[SUCCESS]{ANSI.RESET} Synchronized {len(target_data)} keys.")
        else:
            print(f"   {ANSI.RED}[FAILED]{ANSI.RESET} Sync failed for {full_path}")

    print(f"\n{ANSI.GREEN}[OK] Vault Synchronization Task Completed.{ANSI.RESET}")

if __name__ == "__main__":
    main()
