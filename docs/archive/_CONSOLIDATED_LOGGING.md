# 📝 Centralized Logging - Complete Guide

> **Consolidated from:** CENTRALIZED_LOGGING_README.md + LOGGING_IMPLEMENTATION_SUMMARY.md

## 🎯 Overview

Advanced centralized logging infrastructure for all AM Portfolio services with JSON formatting, correlation tracking, and performance monitoring.

---

## ✅ Fixed Issues

### 1. Import Path Conflicts
- **Problem:** Services couldn't import shared logging
- **Solution:** Added `sys.path` manipulation in services
- **Result:** All services successfully import from `shared/logging/`

### 2. Module Structure
- **Problem:** Python couldn't find logging modules
- **Solution:** Proper `__init__.py` hierarchy
- **Result:** Clean imports: `from shared.logging import initialize_logging`

### 3. Configuration
- **Problem:** Services used different log formats
- **Solution:** Centralized `LogConfig` with environment-based settings
- **Result:** JSON in production, structured in development

---

## 📁 Structure

```
shared/
└── logging/
    ├── __init__.py          # Main exports
    ├── setup.py             # Initialization utilities
    ├── logger.py            # Core logging classes
    ├── config.py            # Configuration management
    └── middleware.py        # FastAPI middleware
```

---

## 🚀 Usage

### Basic Setup (Any Service)

```python
import sys
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from shared.logging import initialize_logging, get_logger

# Initialize logging
initialize_logging("am-auth-tokens")  # or "am-user-management"

# Get logger
logger = get_logger(__name__)

# Use it
logger.info("User registered", extra={"user_id": user_id, "email": email})
```

### FastAPI Integration

```python
from shared.logging import initialize_logging
from shared.logging.middleware import setup_fastapi_logging

# Initialize
initialize_logging("am-auth-tokens")

# Add middleware
app = FastAPI()
setup_fastapi_logging(app, service_name="am-auth-tokens")
```

---

## 🎛️ Configuration

### Environment Variables

```bash
# Log Format
LOG_FORMAT=json              # or "structured" for development
LOG_CONSOLE=true             # Output to console
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR

# File Output (optional)
LOG_FILE_PATH=/app/logs/service.log
LOG_MAX_FILE_SIZE=50000000   # 50MB
LOG_BACKUP_COUNT=10

# Features
ENABLE_CORRELATION=true      # Track requests across services
ENABLE_PERFORMANCE=true      # Track execution times
```

### Service-Specific Config

```python
from shared.logging import LogConfig, initialize_logging

config = LogConfig(
    service_name="am-auth-tokens",
    log_level="INFO",
    log_format="json",
    console_output=True,
    file_output=False,
    enable_correlation=True,
    enable_performance=True
)

initialize_logging("am-auth-tokens", config)
```

---

## 📊 Log Formats

### JSON Format (Production)

```json
{
  "timestamp": "2025-11-11T18:54:43.030768Z",
  "level": "INFO",
  "logger": "am-auth-tokens.main",
  "message": "User logged in successfully",
  "service": "am-auth-tokens",
  "environment": "production",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "correlation_id": "abc123",
  "request_id": "xyz789",
  "execution_time_ms": 234
}
```

### Structured Format (Development)

```
2025-11-11 18:54:43 | INFO | am-auth-tokens.main | User logged in successfully
  user_id: 550e8400-e29b-41d4-a716-446655440000
  email: user@example.com
  execution_time_ms: 234
```

---

## 🔍 Features

### 1. Correlation Tracking
Tracks requests across multiple services:

```python
logger.info("Processing request", extra={
    "correlation_id": request.headers.get("X-Correlation-ID"),
    "request_id": request.headers.get("X-Request-ID")
})
```

### 2. Performance Monitoring
Automatically tracks execution time:

```python
# Middleware automatically adds:
# - request_start_time
# - request_end_time
# - execution_time_ms
```

### 3. Contextual Information
Every log includes:
- Service name
- Environment (dev/prod)
- Module, function, line number
- Thread and process ID
- User context (if available)

---

## 🧪 Quick Setup Functions

### Development
```python
from shared.logging import quick_setup_development

logger = quick_setup_development("am-auth-tokens")
# → DEBUG level, structured format, console only
```

### Production
```python
from shared.logging import quick_setup_production

logger = quick_setup_production("am-auth-tokens", "/var/log/service.log")
# → INFO level, JSON format, file + console
```

### Testing
```python
from shared.logging import quick_setup_testing

logger = quick_setup_testing("am-auth-tokens")
# → WARNING level, minimal output
```

---

## 📈 Docker Integration

### In docker-compose.yml

```yaml
services:
  am-auth-tokens:
    environment:
      - LOG_FORMAT=json
      - LOG_CONSOLE=true
      - LOG_LEVEL=INFO
      - ENVIRONMENT=docker
    volumes:
      - ../shared:/app/shared  # Mount shared logging
```

### Viewing Logs

```bash
# All services with JSON parsing
docker-compose logs -f | jq .

# Specific service
docker-compose logs -f am-auth-tokens | jq .

# Filter by level
docker-compose logs -f | grep "ERROR"
```

---

## 🎓 Best Practices

### 1. Use Extra Fields
```python
# ✅ Good: Structured data
logger.info("User action", extra={
    "action": "login",
    "user_id": user_id,
    "ip_address": ip
})

# ❌ Bad: String concatenation
logger.info(f"User {user_id} logged in from {ip}")
```

### 2. Appropriate Levels
```python
logger.debug("Processing started")      # Debugging info
logger.info("User logged in")           # Normal operations
logger.warning("Rate limit approaching") # Potential issues
logger.error("Database connection failed") # Errors
```

### 3. Don't Log Sensitive Data
```python
# ❌ Bad: Logs password
logger.info("Login attempt", extra={"password": password})

# ✅ Good: No sensitive data
logger.info("Login attempt", extra={"email": email})
```

### 4. Use Correlation IDs
```python
correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
logger.info("Request received", extra={"correlation_id": correlation_id})
```

---

## 🔧 Troubleshooting

### Import Errors

```python
# Add this at top of main.py:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))
```

### No Logs Appearing

```bash
# Check LOG_LEVEL
LOG_LEVEL=DEBUG  # Set to DEBUG temporarily

# Check console output is enabled
LOG_CONSOLE=true
```

### JSON Parse Errors

```bash
# Some logs might not be JSON (startup messages)
# Filter for valid JSON:
docker-compose logs -f | grep "^{" | jq .
```

---

## 📚 Related Files

- `shared/logging/` - Logging infrastructure
- `docker-compose.yml` - Environment configuration
- `.github/copilot-instructions.md` - Usage patterns

---

**🎉 Centralized logging is operational across all services!**
