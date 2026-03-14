import subprocess
import sys
import os

def run_command(command, cwd=None):
    print(f"\n--- Running: {command} ---")
    result = subprocess.run(command, shell=True, cwd=cwd)
    return result.returncode

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Run Logging Integration Tests
    logging_rc = run_command("poetry run test-logging", cwd=base_dir)
    
    # 2. Run Database Connection Test
    db_rc = run_command("poetry run db-test", cwd=base_dir)
    
    # 3. Run Service Unit/Integration Tests (Example for user-management)
    um_rc = run_command("pytest am/am-user-management/tests", cwd=base_dir)
    
    if logging_rc == 0 and db_rc == 0 and um_rc == 0:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
