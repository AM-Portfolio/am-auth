import argparse
import os
import sys

# --- Bootstrap am-scripts ---
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
am_repos_root = os.path.dirname(repo_root)
am_scripts_src = os.path.join(am_repos_root, "am-scripts", "src")

if os.path.exists(am_scripts_src):
    if am_scripts_src not in sys.path:
        sys.path.insert(0, am_scripts_src)
else:
    print(f"Error: am-scripts repository not found at {am_scripts_src}")
    print("Please clone am-scripts into the same parent directory as am-auth.")
    sys.exit(1)

from am_scripts.deploy import main_deploy_logic
from am_scripts.utils import setup_logger, load_config, parse_env

logger = setup_logger("AM_Auth_Deploy")

def auth_helm_overrides(app_vars, helm_args):
    """
    am-auth specific Helm overrides.
    """
    def transform_url(url, target_host):
        if "localhost" in url:
            return url.replace("localhost", target_host)
        return url

    # Database
    if "DATABASE_URL" in app_vars:
        db_url = transform_url(app_vars["DATABASE_URL"], "postgresql.infra.svc.cluster.local")
        helm_args.append(f'--set apiGateway.env.DATABASE_URL="{db_url}"')
        helm_args.append(f'--set userManagement.env.DATABASE_URL="{db_url}"')
        helm_args.append(f'--set authTokens.env.DATABASE_URL="{db_url}"')

    # Redis
    if "REDIS_URL" in app_vars:
        redis_url = transform_url(app_vars["REDIS_URL"], "redis.infra.svc.cluster.local")
        helm_args.append(f'--set userManagement.env.REDIS_URL="{redis_url}"')

    # Secrets
    if "JWT_SECRET" in app_vars:
        helm_args.append(f'--set apiGateway.env.JWT_SECRET="{app_vars["JWT_SECRET"]}"')
        helm_args.append(f'--set authTokens.env.JWT_SECRET="{app_vars["JWT_SECRET"]}"')
    
    if "SECRET_KEY" in app_vars:
        helm_args.append(f'--set userManagement.env.SECRET_KEY="{app_vars["SECRET_KEY"]}"')
    
    if "JWT_SECRET_KEY" in app_vars:
            helm_args.append(f'--set userManagement.env.JWT_SECRET_KEY="{app_vars["JWT_SECRET_KEY"]}"')

    if "INTERNAL_JWT_SECRET" in app_vars:
            helm_args.append(f'--set authTokens.env.INTERNAL_JWT_SECRET="{app_vars["INTERNAL_JWT_SECRET"]}"')

    # CLS - Enforce internal K8s URL
    cls_url = "http://am-logging.am-apps-local.svc.cluster.local:8000"
    helm_args.append(f'--set userManagement.env.CLS_URL="{cls_url}"')
    helm_args.append(f'--set authTokens.env.CLS_URL="{cls_url}"')
    
    # Feature Flags (Defaults)
    helm_args.append('--set userManagement.env.USER_MGMT_PERSIST_TO_DB="true"')
    helm_args.append('--set authTokens.env.AUTH_TOKENS_PERSIST_TO_DB="false"')

def main():
    config_path = os.path.join(repo_root, "deploy_config.json")
    env_path = os.path.join(repo_root, ".env.deploy")
    
    # Load Configs
    config = load_config(config_path)
    env_vars = parse_env(env_path)
    
    # Load App Secrets
    app_env_path = os.path.join(repo_root, "am", ".env")
    app_env_vars = parse_env(app_env_path) if os.path.exists(app_env_path) else {}

    # Defaults
    defaults = {
        "namespace_prefix": env_vars.get("NAMESPACE_PREFIX", config.get("namespace_prefix", "am")),
        "kind_cluster": env_vars.get("KIND_CLUSTER_NAME", "am-preprod"),
        "skip_load": env_vars.get("SKIP_KIND_LOAD", "false").lower() == "true",
        "run_docker": env_vars.get("RUN_DOCKER", "false").lower() == "true",
        "skip_build": env_vars.get("SKIP_BUILD", "false").lower() == "true"
    }

    # Arguments
    parser = argparse.ArgumentParser(description="Build and deploy AM Auth services locally.")
    parser.add_argument("--skip-build", "-k", action="store_true", default=defaults["skip_build"], help="Skip Docker builds")
    parser.add_argument("--build-only", "-b", action="store_true", help="Only build Docker images, do not deploy")
    parser.add_argument("--deploy-only", "-d", action="store_true", help="Only deploy via Helm, skip builds")
    parser.add_argument("--services", "-s", type=str, help="Comma-separated list of services to process")
    parser.add_argument("--namespace-prefix", "-p", type=str, default=defaults["namespace_prefix"], help=f"Prefix for namespaces")
    parser.add_argument("--kind-cluster-name", type=str, default=defaults["kind_cluster"], help=f"Name of the KIND cluster")
    parser.add_argument("--skip-kind-load", action="store_true", default=defaults["skip_load"], help="Skip automatically loading images into KIND")
    parser.add_argument("--run-docker", action="store_true", default=defaults["run_docker"], help="Run in Docker instead of K8s")
    
    args = parser.parse_args()

    # Run Main Logic
    main_deploy_logic(config, env_vars, app_env_vars, repo_root, args, helm_overrides_callback=auth_helm_overrides)

if __name__ == "__main__":
    main()
