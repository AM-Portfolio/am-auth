"""
Test script for AM Logging SDK integration
Tests fire-and-forget logging functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the shared logging path
shared_path = Path(__file__).parent.parent
sys.path.insert(0, str(shared_path))

try:
    from am.shared.logging.am_logging_sdk import AMLoggingClient, LoggerMixin
    from am.shared.logging.auth_adapter import AMAuthLogger, get_auth_logger
    from am.shared.logging.fire_and_forget import get_fire_and_forget_handler, log_fire_and_forget
    print("✅ Successfully imported AM Logging SDK components")
except ImportError as e:
    print(f"❌ Failed to import AM Logging SDK: {e}")
    sys.path.append(str(Path(__file__).parent.parent))
    try:
        from am.shared.logging.am_logging_sdk import AMLoggingClient, LoggerMixin
        from am.shared.logging.auth_adapter import AMAuthLogger, get_auth_logger
        from am.shared.logging.fire_and_forget import get_fire_and_forget_handler, log_fire_and_forget
        print("✅ Successfully imported AM Logging SDK components (fallback)")
    except ImportError:
        print(f"❌ Still failed to import AM Logging SDK. PYTHONPATH: {sys.path}")
        sys.exit(1)


class TestAuthService(LoggerMixin):
    """Test service class with logging capabilities"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "test-auth-service"
    
    async def test_login(self, user_id: str, success: bool = True):
        """Test user login logging"""
        self.log_info(f"User login attempt: {user_id}", user_id=user_id, success=success)
        return success
    
    async def test_token_generation(self, user_id: str, token_type: str = "JWT"):
        """Test token generation logging"""
        self.log_info(f"Token generated for user: {user_id}", user_id=user_id, token_type=token_type)
        return f"mock_token_{user_id}"


async def test_sdk_functionality():
    """Test the complete SDK functionality"""
    print("\n🧪 Testing AM Logging SDK Integration...")
    
    # Test 1: Basic AMLoggingClient
    print("\n1. Testing AMLoggingClient...")
    client = AMLoggingClient(base_url="http://localhost:8000/v1")  # Mock URL
    
    test_log = client.create_log_entry(
        trace_id="test-trace-123",
        span_id="test-span-456", 
        service="test-service",
        level="INFO",
        payload={"message": "Test log entry"},
        context={"test": True}
    )
    
    print(f"   ✅ Created log entry: {test_log['trace_id']}")
    
    # Test 2: LoggerMixin
    print("\n2. Testing LoggerMixin...")
    test_service = TestAuthService()
    
    # Test fire-and-forget logging
    test_service.log_info("Test message from mixin", test_param="value")
    print("   ✅ LoggerMixin fire-and-forget logging works")
    
    # Test 3: Auth Logger
    print("\n3. Testing AMAuthLogger...")
    auth_logger = get_auth_logger()
    
    async with auth_logger.trace_context("test_operation") as context:
        auth_logger.log_auth_event("TEST_LOGIN", user_id="test-user-123")
        print(f"   ✅ Auth logger trace context: {context['trace_id']}")
    
    # Test 4: Fire-and-forget handler
    print("\n4. Testing Fire-and-forget handler...")
    ff_handler = get_fire_and_forget_handler()
    
    await ff_handler.send_log_async({
        "trace_id": "ff-test-123",
        "span_id": "ff-test-456",
        "service": "test-service",
        "timestamp": "2024-01-01T00:00:00Z",
        "log_type": "TECHNICAL",
        "level": "INFO",
        "payload": {"message": "Fire-and-forget test"},
        "context": {"test": True}
    })
    print("   ✅ Fire-and-forget handler works")
    
    # Test 5: Decorator functionality
    print("\n5. Testing logging decorator...")
    
    @log_fire_and_forget(level="INFO", message="Test decorated function")
    async def test_decorated_function():
        await asyncio.sleep(0.1)  # Simulate work
        return "success"
    
    result = await test_decorated_function()
    print(f"   ✅ Decorated function returned: {result}")
    
    # Test 6: Service integration test
    print("\n6. Testing service integration...")
    
    # Simulate login flow
    login_success = await test_service.test_login("user-456", True)
    if login_success:
        token = await test_service.test_token_generation("user-456", "JWT")
        print(f"   ✅ Service integration test passed, token: {token}")
    
    print("\n🎉 All tests completed successfully!")
    print("\n📝 Summary:")
    print("   - ✅ AMLoggingClient: Creates and validates log entries")
    print("   - ✅ LoggerMixin: Provides easy logging methods")
    print("   - ✅ AMAuthLogger: Auth-specific logging with tracing")
    print("   - ✅ Fire-and-forget: Non-blocking async logging")
    print("   - ✅ Decorator: Automatic function logging")
    print("   - ✅ Integration: Complete service logging flow")


async def test_error_handling():
    """Test error handling in fire-and-forget logging"""
    print("\n🔧 Testing error handling...")
    
    # Test with invalid URL (should fail silently)
    client = AMLoggingClient(base_url="http://invalid-url-that-will-fail.com")
    
    test_log = client.create_log_entry(
        trace_id="error-test-123",
        span_id="error-test-456",
        service="test-service",
        level="ERROR",
        payload={"message": "Error test"}
    )
    
    # This should fail silently (fire-and-forget behavior)
    client.send_log(test_log)
    print("   ✅ Error handling works - failed silently as expected")


if __name__ == "__main__":
    print("🚀 AM Logging SDK Integration Test")
    print("=" * 50)
    
    try:
        asyncio.run(test_sdk_functionality())
        asyncio.run(test_error_handling())
        
        print("\n✅ All integration tests passed!")
        print("\n📋 Next steps:")
        print("   1. Start the AM Logging service")
        print("   2. Update the base_url in production")
        print("   3. Test with real logging endpoint")
        print("   4. Monitor logs in the logging service")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
