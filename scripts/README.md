# AM Portfolio Developer Scripts

This directory contains utility scripts for local development, testing, and deployment. These scripts are registered as Poetry commands in `pyproject.toml`.

## Quick Start
Run these commands from the `am-auth` root directory using `poetry run <command>`.

| Command | Script | Description |
| :--- | :--- | :--- |
| `setup` | `setup.py` | **One-command Setup**: Syncs SDKs and Deploys everything. |
| `deploy-local` | `deploy_local.py` | Build Docker images and deploy via Helm. |
| `test-logging` | `test_logging_integration.py` | Integration tests for the central logging system. |
| `db-test` | `test_db_connection.py` | Verify connection to the local PostgreSQL instance. |
| `test-all` | `run_all_tests.py` | Run logging, DB, and service tests in sequence. |

---

## Command Reference

### `poetry run deploy-local`
The primary tool for local Kubernetes deployment.
- **Default**: Builds all images (`am-auth`, `am-logging`) and deploys both Helm charts.
- **Short Flags**:
    - `-s <svc>`: `--services` (e.g., `am-auth-tokens`).
    - `-b`: `--build-only` (skip deploy).
    - `-d`: `--deploy-only` (skip build).
    - `-k`: `--skip-build` (same as `-d`, for convenience).
    - `-p`: `--namespace-prefix` (default: `am`).

### `poetry run test-logging`
Tests the integration between authorized services and the `am-logging` service.
- Verifies that correlation IDs are passed.
- Verifies that logs are correctly sent to the central collector.

### `poetry run db-test`
A lightweight script to verify that your local environment (or containers) can reach the PostgreSQL database using the credentials from `generated-credentials.txt`.

### `poetry run test-all`
A master test runner that orchestrates:
1. Logging Integration Tests.
2. Database Connection Verification.
3. Service-level Pytest suites (defined in the script).

---

## Directory Structure
- `scripts/deploy_local.py`: Core deployment logic.
- `scripts/test_logging_integration.py`: Logging SDK validation.
- `scripts/test_db_connection.py`: Database health check.
- `scripts/run_all_tests.py`: Test orchestration.
- `scripts/__init__.py`: Required for Poetry package registration.
