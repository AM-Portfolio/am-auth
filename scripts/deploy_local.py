import os
import subprocess
import sys
import argparse

def run_command(command, cwd=None):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(description="Build and deploy AM services locally.")
    parser.add_argument("--skip-build", "-k", action="store_true", help="Skip Docker builds")
    parser.add_argument("--build-only", "-b", action="store_true", help="Only build Docker images, do not deploy")
    parser.add_argument("--deploy-only", "-d", action="store_true", help="Only deploy via Helm, skip builds")
    parser.add_argument("--services", "-s", type=str, help="Comma-separated list of services to process")
    parser.add_argument("--namespace-prefix", "-p", type=str, default="am", help="Prefix for namespaces (default: am)")
    args = parser.parse_args()

    # Use paths relative to the script location (am-auth/scripts/deploy_local.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    am_auth_root = os.path.dirname(script_dir)
    repos_root = os.path.dirname(am_auth_root)
    
    all_services = [
        {"name": "am-api-gateway", "context": os.path.join(am_auth_root, "am", "am-api-gateway"), "repo": "am-auth"},
        {"name": "am-auth-tokens", "context": os.path.join(am_auth_root, "am", "am-auth-tokens"), "repo": "am-auth"},
        {"name": "am-user-management", "context": os.path.join(am_auth_root, "am", "am-user-management"), "repo": "am-auth"},
        {"name": "am-logging-svc", "context": os.path.join(repos_root, "am-logging", "service"), "repo": "am-logging"}
    ]

    # Filter services if requested
    target_services = all_services
    if args.services:
        target_names = [n.strip() for n in args.services.split(",")]
        target_services = [s for s in all_services if s["name"] in target_names]
        if not target_services:
            print(f"Error: No matching services found for: {args.services}")
            sys.exit(1)

    # 1. Build Docker Images
    if not (args.skip_build or args.deploy_only):
        for svc in target_services:
            print(f"\n--- Building {svc['name']} ---")
            if svc["repo"] == "am-auth":
                shared_src = os.path.join(am_auth_root, "am", "shared")
                shared_dest = os.path.join(svc['context'], "shared")
                if os.path.exists(shared_src):
                    run_command(f'xcopy "{shared_src}" "{shared_dest}" /E /I /Y')
            
            run_command(f'docker build -t "local/{svc["name"]}:latest" "{svc["context"]}"')

    # 2. Deploy via Helm
    if not args.build_only:
        # Check which charts need deploying
        repos_to_deploy = set(s["repo"] for s in target_services)
        
        if "am-logging" in repos_to_deploy:
            print("\n--- Deploying am-logging ---")
            logging_helm = os.path.join(repos_root, "am-logging", "helm")
            run_command(f'helm upgrade --install am-logging "{logging_helm}" '
                        f'-f "{os.path.join(logging_helm, "values.yaml")}" '
                        f'-f "{os.path.join(logging_helm, "values-local.yaml")}" '
                        f'--namespace {args.namespace_prefix}-logging-local --create-namespace')

        if "am-auth" in repos_to_deploy:
            print("\n--- Deploying am-auth ---")
            auth_helm = os.path.join(am_auth_root, "helm", "am-auth")
            run_command(f'helm upgrade --install am-auth "{auth_helm}" '
                        f'-f "{os.path.join(auth_helm, "values.yaml")}" '
                        f'-f "{os.path.join(auth_helm, "values-local.yaml")}" '
                        f'--namespace {args.namespace_prefix}-apps-local --create-namespace')

    print("\n✅ Local deployment task completed.")

if __name__ == "__main__":
    main()
