# Centralized Advanced Logging for AM Portfolio Services

This document describes the centralized logging infrastructure implemented for the AM Portfolio services (`am-auth-tokens` and `am-user-management`).

## 🎯 Overview

The centralized logging system provides advanced features including:

- **Structured JSON Logging**: All logs are formatted in JSON for easy parsing and analysis
- **Correlation IDs**: Automatic request tracking across service boundaries
- **Performance Monitoring**: Built-in execution time tracking for functions and API calls
- **FastAPI Integration**: Automatic request/response logging with correlation context
- **Configurable Output**: Support for console, file, and multiple log formats
- **Service-Specific Configuration**: Different log levels and settings per service
- **Production Ready**: Log rotation, sampling, and optimized performance

## 📁 Architecture

```
shared/
└── logging/
    ├── __init__.py          # Main exports and convenience functions
    ├── logger.py            # Core logging infrastructure
    ├── middleware.py        # FastAPI middleware for request tracking
    ├── config.py            # Service-specific configuration management
    └── setup.py             # Initialization and setup utilities
```

## 🚀 Quick Start

### Development Setup

```python
from shared.logging import quick_setup_development, get_logger

# Initialize logging for development
quick_setup_development("my-service")

# Get a logger and start logging
logger = get_logger("my-service.module")
logger.info("Hello world!", extra={"user_id": "123", "action": "login"})
```

### Production Setup

```python
from shared.logging import quick_setup_production, get_logger

# Initialize logging for production
quick_setup_production("my-service", "/var/log/my-service.log")

# Use structured logging
logger = get_logger("my-service")
logger.info("User login successful", extra={
    "user_id": "123",
    "ip_address": "192.168.1.1",
    "duration_ms": 150
})
```

### FastAPI Integration

```python
from fastapi import FastAPI
from shared.logging import initialize_auth_tokens_logging
from shared.logging.middleware import LoggingMiddleware

# Initialize logging
initialize_auth_tokens_logging()

# Create FastAPI app
app = FastAPI()

# Add logging middleware
app.add_middleware(
    LoggingMiddleware,
    service_name="am-auth-tokens",
    exclude_paths=["/health", "/metrics"]
)
```

## 🔧 Configuration

### Environment Variables

#### Global Settings
- `LOG_FORMAT`: `json` | `structured` | `text` (default: `json`)
- `LOG_CONSOLE`: `true` | `false` (default: `true`)
- `LOG_ENABLE_CORRELATION`: `true` | `false` (default: `true`)
- `LOG_ENABLE_PERFORMANCE`: `true` | `false` (default: `true`)
- `ENVIRONMENT`: `development` | `staging` | `production`

#### Auth Tokens Service
- `AUTH_TOKENS_LOG_LEVEL`: `DEBUG` | `INFO` | `WARNING` | `ERROR`
- `AUTH_TOKENS_FILE_LOGGING`: `true` | `false`
- `AUTH_TOKENS_LOG_FILE`: Path to log file
- `AUTH_TOKENS_OAUTH_DEBUG`: `true` | `false`
- `AUTH_TOKENS_JWT_DEBUG`: `true` | `false`

#### User Management Service
- `USER_MGMT_LOG_LEVEL`: `DEBUG` | `INFO` | `WARNING` | `ERROR`
- `USER_MGMT_FILE_LOGGING`: `true` | `false`
- `USER_MGMT_LOG_FILE`: Path to log file
- `USER_MGMT_DB_DEBUG`: `true` | `false`
- `USER_MGMT_EMAIL_DEBUG`: `true` | `false`

## 📋 Log Format Examples

### JSON Format (Production)
```json
{
  "timestamp": "2025-10-10T10:30:45.123Z",
  "level": "INFO",
  "logger": "am-auth-tokens.google_auth",
  "message": "Google token verification completed",
  "service": "am-auth-tokens",
  "correlation_id": "abc123-def456-789",
  "request_id": "req-987654321",
  "user_id": "user-12345",
  "duration_ms": 150.25,
  "user_email": "user@example.com",
  "verification_method": "google_oauth"
}
```

### Structured Format (Development)
```
[2025-10-10 10:30:45 UTC] INFO     am-auth-tokens:google_auth - Google token verification completed [correlation=abc123, user=user-12345, duration=150ms]
```

## 🛠 Advanced Features

### Automatic Performance Tracking

```python
from shared.logging import log_execution_time, log_async_execution_time

@log_execution_time("my-service.operations")
def slow_operation():
    # This function's execution time will be automatically logged
    pass

@log_async_execution_time("my-service.async_operations") 
async def async_operation():
    # Async function timing
    pass
```

### Logger Mixin for Classes

```python
from shared.logging import LoggerMixin

class UserService(LoggerMixin):
    def create_user(self, user_data):
        self.log_info("Creating new user", extra={"email": user_data.email})
        try:
            # Business logic here
            self.log_info("User created successfully", extra={"user_id": user.id})
        except Exception as e:
            self.log_error("User creation failed", exc_info=True, extra={"error": str(e)})
```

### Correlation Context Management

```python
from shared.logging import set_correlation_context, get_logger

# Set context for request tracking
set_correlation_context(
    correlation_id="abc-123",
    request_id="req-456", 
    user_id="user-789"
)

# All subsequent logs will include this context
logger = get_logger("my-service")
logger.info("Processing request")  # Will include correlation info
```

## 🐳 Docker Integration

The `docker-compose.yml` is configured to:

1. Mount the shared logging infrastructure
2. Create log volumes for persistent storage
3. Set appropriate environment variables
4. Enable structured JSON logging

Log files are stored in:
- `./logs/auth-tokens/` - Auth tokens service logs
- `./logs/user-management/` - User management service logs

## 🔍 Monitoring and Analysis

### Log Aggregation
JSON logs can be easily ingested by:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Fluentd/Fluent Bit**
- **Splunk**
- **DataDog**
- **New Relic**

### Key Fields for Filtering
- `service`: Service name (`am-auth-tokens`, `am-user-management`)
- `correlation_id`: Request tracking across services
- `user_id`: User-specific operations
- `level`: Log severity
- `duration_ms`: Performance analysis
- `error_type`: Error categorization

## 📊 Performance Considerations

### Log Sampling
For high-traffic scenarios, enable sampling:
```python
config = LogConfig(
    enable_sampling=True,
    sampling_rate=0.1  # Log only 10% of debug messages
)
```

### File Rotation
Automatic log rotation prevents disk space issues:
- Size-based rotation (default: 10MB files, 5 backups)
- Time-based rotation (daily, hourly options)

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the shared directory is in your Python path
2. **FastAPI Middleware Not Available**: The middleware gracefully handles missing FastAPI imports
3. **Log Files Not Created**: Check directory permissions and paths
4. **Performance Impact**: Adjust log levels and enable sampling for high-traffic services

### Debug Mode
Enable debug logging to troubleshoot issues:
```bash
export LOG_LEVEL=DEBUG
export AUTH_TOKENS_LOG_LEVEL=DEBUG
export USER_MGMT_LOG_LEVEL=DEBUG
```

## 🔄 Migration from Old Logging

### Before (Basic Logging)
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Simple message")
```

### After (Centralized Logging)
```python
from shared.logging import get_logger, initialize_auth_tokens_logging

initialize_auth_tokens_logging()
logger = get_logger("am-auth-tokens.module")
logger.info("Structured message", extra={
    "user_id": "123",
    "action": "login",
    "duration_ms": 150
})
```

## 📈 Benefits

1. **Consistency**: Uniform logging format across all services
2. **Traceability**: Request tracking with correlation IDs
3. **Performance**: Built-in execution time monitoring
4. **Debugging**: Rich context and structured data
5. **Production Ready**: Rotation, sampling, and optimization
6. **Integration**: Easy setup with existing FastAPI applications
7. **Scalability**: Configurable for different environments and traffic levels

## 🤝 Contributing

When adding new services:
1. Add service configuration to `config.py`
2. Create service-specific setup function
3. Update environment variable documentation
4. Test with different log formats and levels

## 📝 Example Integration

See the integrated examples in:
- `am-auth-tokens/main.py` - FastAPI app with middleware
- `am-auth-tokens/app/services/google_auth_service.py` - Service class with logging
- `am-user-management/main.py` - User management service integration
- `am-user-management/modules/.../repositories/sqlalchemy_user_repository.py` - Repository logging