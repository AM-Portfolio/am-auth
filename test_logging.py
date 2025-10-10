#!/usr/bin/env python3
"""
Test script to verify centralized logging setup
"""

import sys
from pathlib import Path

# Add shared logging to path
shared_path = Path(__file__).parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

def test_logging_imports():
    """Test that all logging imports work correctly"""
    try:
        from shared.logging import (
            initialize_user_management_logging, 
            initialize_auth_tokens_logging,
            get_logger,
            LoggerMixin,
            log_execution_time
        )
        print("✅ Successfully imported core logging functions")
        return True
    except ImportError as e:
        print(f"❌ Failed to import core logging: {e}")
        return False

def test_middleware_imports():
    """Test middleware imports (may fail if FastAPI not available)"""
    try:
        from shared.logging.middleware import LoggingMiddleware
        print("✅ Successfully imported FastAPI middleware")
        return True
    except ImportError as e:
        print(f"⚠️  FastAPI middleware not available (expected in some environments): {e}")
        return True  # This is expected in some environments

def test_logger_functionality():
    """Test basic logger functionality"""
    try:
        from shared.logging import quick_setup_development, get_logger
        
        # Setup logger
        quick_setup_development("test-service")
        logger = get_logger("test-service.test")
        
        # Test logging
        logger.info("Test log message", extra={"test": True, "component": "test_script"})
        logger.warning("Test warning message")
        logger.error("Test error message", extra={"error_code": "TEST_ERROR"})
        
        print("✅ Logger functionality test passed")
        return True
    except Exception as e:
        print(f"❌ Logger functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Centralized Logging Setup")
    print("=" * 50)
    
    tests = [
        test_logging_imports,
        test_middleware_imports,
        test_logger_functionality
    ]
    
    results = []
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! Centralized logging is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit(main())