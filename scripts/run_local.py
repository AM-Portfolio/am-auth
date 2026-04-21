import sys
import os

# --- Bootstrap am-scripts ---
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
am_repos_root = os.path.dirname(repo_root)
am_scripts_src = os.path.join(am_repos_root, "am-scripts", "src")

# Ensure am-scripts is in the python path to load its shared templates
if os.path.exists(am_scripts_src) and am_scripts_src not in sys.path:
    sys.path.insert(0, am_scripts_src)
    
try:
    from am_scripts.run_local import run_service
except ImportError:
    print(f"Error: am-scripts repository not found at {am_scripts_src}")
    print("Please clone am-scripts into the same parent directory to use the shared runner template.")
    sys.exit(1)

# --- Pre-configured Entry Points for pyproject.toml 'poetry run' scripts ---

def run_user():
    """Entry point for AM User Management."""
    target = os.path.abspath(os.path.join(repo_root, "am", "am-user-management"))
    run_service("AM User Management API", target, 8000, am_repos_root, repo_root, app_entry="main:app")

def run_auth():
    """Entry point for AM Auth Tokens."""
    target = os.path.abspath(os.path.join(repo_root, "am", "am-auth-tokens"))
    run_service("AM Auth Tokens API", target, 8001, am_repos_root, repo_root, app_entry="main:app")

if __name__ == "__main__":
    # Allows developers to run arbitrary custom models & entry modules 
    # Example: python scripts/run_local.py am-user-management 8080 my_custom_app:entry
    if len(sys.argv) > 2:
        svc_dir = sys.argv[1]
        port_num = sys.argv[2]
        entry_module = sys.argv[3] if len(sys.argv) > 3 else "main:app"
        
        target_path = os.path.abspath(os.path.join(repo_root, "am", svc_dir))
        run_service(f"Custom Model ({svc_dir})", target_path, port_num, am_repos_root, repo_root, app_entry=entry_module)
    else:
        print("Template Usage: python run_local.py <service_dir_name> <port> [app_entry]")
        print("Example: python run_local.py am-user-management 8080 core.main:app")
        print("Alternatively, run pre-configured via poetry: poetry run run-user OR poetry run run-auth")
