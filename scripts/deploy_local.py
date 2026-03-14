import argparse
import os
import subprocess
import sys
import tempfile
from typing import List

def run_command(command, cwd=None):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def discover_kind_nodes(cluster_name: str) -> List[str]:
    """Return KIND node container names for the given cluster."""
    if not cluster_name:
        return []

    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("Docker CLI not available; skipping KIND image load.")
        return []

    if result.returncode != 0:
        print("Unable to list docker containers; skipping KIND image load.")
        return []

    prefix = f"{cluster_name}-"
    return [name.strip() for name in result.stdout.splitlines() if name.strip().startswith(prefix)]


def load_image_into_kind(image_tag: str, cluster_name: str) -> None:
    nodes = discover_kind_nodes(cluster_name)
    if not nodes:
        print(
            f"No KIND nodes detected for cluster '{cluster_name}'. "
            "Skipping automatic image load."
        )
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = os.path.join(tmpdir, "image.tar")
        print(f"Saving {image_tag} to temporary tarball ...")
        save_result = subprocess.run(["docker", "save", image_tag, "-o", tar_path])
        if save_result.returncode != 0:
            print("Failed to save Docker image; skipping KIND image load.")
            return

        for node in nodes:
            print(f"Loading {image_tag} into {node} ...")
            with open(tar_path, "rb") as tar_file:
                load_result = subprocess.run(
                    ["docker", "exec", "-i", node, "ctr", "-n", "k8s.io", "image", "import", "-"],
                    stdin=tar_file,
                )
            if load_result.returncode != 0:
                print(
                    f"Warning: failed to load {image_tag} into {node} "
                    f"(exit code {load_result.returncode})."
                )


def main():
    parser = argparse.ArgumentParser(description="Build and deploy AM services locally.")
    parser.add_argument("--skip-build", "-k", action="store_true", help="Skip Docker builds")
    parser.add_argument("--build-only", "-b", action="store_true", help="Only build Docker images, do not deploy")
    parser.add_argument("--deploy-only", "-d", action="store_true", help="Only deploy via Helm, skip builds")
    parser.add_argument("--services", "-s", type=str, help="Comma-separated list of services to process")
    parser.add_argument("--namespace-prefix", "-p", type=str, default="am", help="Prefix for namespaces (default: am)")
    parser.add_argument(
        "--kind-cluster-name",
        type=str,
        default="am-preprod",
        help="Name of the KIND cluster whose nodes should receive images (set empty to skip)",
    )
    parser.add_argument(
        "--skip-kind-load",
        action="store_true",
        help="Skip automatically loading the Docker images into KIND nodes",
    )
    args = parser.parse_args()

    # Use paths relative to the script location (am-auth/scripts/deploy_local.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    am_auth_root = os.path.dirname(script_dir)
    repos_root = os.path.dirname(am_auth_root)
    
    all_services = [
        {"name": "am-api-gateway", "context": os.path.join(am_auth_root, "am", "am-api-gateway"), "repo": "am-auth"},
        {"name": "am-auth-tokens", "context": os.path.join(am_auth_root, "am", "am-auth-tokens"), "repo": "am-auth"},
        {"name": "am-user-management", "context": os.path.join(am_auth_root, "am", "am-user-management"), "repo": "am-auth"}
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
    image_tags = {}

    if not (args.skip_build or args.deploy_only):
        for svc in target_services:
            print(f"\n--- Building {svc['name']} ---")
            if svc["repo"] == "am-auth":
                shared_src = os.path.join(am_auth_root, "am", "shared")
                shared_dest = os.path.join(svc['context'], "shared")
                if os.path.exists(shared_src):
                    run_command(f'xcopy "{shared_src}" "{shared_dest}" /E /I /Y')
            
            image_tag = f'local/{svc["name"]}:latest'
            run_command(f'docker build -t "{image_tag}" "{svc["context"]}"')
            image_tags[svc["name"]] = image_tag

    if not args.skip_kind_load:
        for svc in target_services:
            tag = image_tags.get(svc["name"], f'local/{svc["name"]}:latest')
            load_image_into_kind(tag, args.kind_cluster_name)

    # 2. Deploy via Helm
    if not args.build_only:
        # Check which charts need deploying
        repos_to_deploy = set(s["repo"] for s in target_services)
        
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
