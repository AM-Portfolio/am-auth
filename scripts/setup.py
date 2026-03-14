import os
import subprocess
import sys

def run_command(command, cwd=None):
    print(f"\n--- Running: {command} ---")
    result = subprocess.run(command, shell=True, cwd=cwd)
    return result.returncode

def main():
    # Paths relative to this script: am-auth/scripts/setup.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    am_auth_root = os.path.dirname(script_dir)
    repos_root = os.path.dirname(am_auth_root)
    am_logging_root = os.path.join(repos_root, "am-logging")

    print("🚀 Starting Full AM Portfolio Setup...")

    # 1. Sync Logging SDKs (if repo exists)
    if os.path.exists(am_logging_root):
        print("\n📦 Found am-logging repo. Synchronizing SDKs...")
        sync_rc = run_command("poetry run generate-and-sync", cwd=am_logging_root)
        if sync_rc != 0:
            print("❌ SDK synchronization failed. Continuing with existing files...")
    else:
        print("\n⚠️ am-logging repo not found. Skipping SDK synchronization.")

    # 2. Deploy Local Infrastructure & Services
    print("\n🏗️  Starting Local Deployment...")
    deploy_rc = run_command("poetry run deploy-local", cwd=am_auth_root)
    
    if deploy_rc == 0:
        print("\n✨ All systems go! Use 'poetry run test-all' to verify.")
    else:
        print("\n❌ Deployment failed.")
        sys.exit(deploy_rc)

if __name__ == "__main__":
    main()
