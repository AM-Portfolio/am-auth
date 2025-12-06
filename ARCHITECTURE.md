# Module Architecture & Organization

## High-Level Architecture

```
AM Portfolio
│
├── 🟦 Shared Infrastructure (ROOT LEVEL)
│   ├── shared/auth/              - JWT validation & security
│   ├── shared/logging/           - Centralized logging
│   └── shared/testing/           - Testing utilities & fixtures
│
├── 🟩 Services
│   ├── am/am-api-gateway/        - API Gateway (port 8000)
│   ├── am/am-user-management/    - User Service (port 8010)
│   ├── am/am-auth-tokens/        - Auth Service (port 8001)
│   ├── am/am-python-internal/    - Python Service (port 8002)
│   └── am/am-java-internal/      - Java Service (port 8003)
│
├── 🟨 Testing
│   └── am/am-tests/              - Integration & E2E tests
│
└── 📚 Documentation
    ├── shared/README.md           - Shared modules guide
    └── SHARED_MODULES_GUIDE.md    - Consolidation plan
```

## Detailed Shared Module Hierarchy

```
shared/
│
├── auth/
│   ├── jwt_utils.py
│   │   ├── JWTValidator
│   │   │   ├── validate_user_token()
│   │   │   ├── validate_service_token()
│   │   │   └── generate_service_token()
│   │   └── Token validation strategies
│   │
│   └── validation.py
│       └── Input validation helpers
│
├── logging/
│   ├── logger.py
│   │   ├── AMLogger (main logger)
│   │   ├── EnhancedJSONFormatter
│   │   └── Advanced logging features
│   │
│   ├── middleware.py
│   │   └── LoggingMiddleware (FastAPI)
│   │
│   ├── config.py
│   │   └── Logging configuration
│   │
│   └── setup.py
│       └── initialize_logging()
│
└── testing/
    ├── utils/
    │   ├── token_generator.py
    │   │   └── TokenGenerator
    │   │       ├── generate_user_token()
    │   │       ├── generate_service_token()
    │   │       ├── generate_expired_token()
    │   │       └── generate_invalid_token()
    │   │
    │   └── test_client.py
    │       ├── get_test_client()
    │       ├── get_sync_test_client()
    │       └── create_headers()
    │
    └── fixtures/
        ├── users.py
        │   ├── create_test_user()
        │   ├── get_test_user_payload()
        │   └── get_test_user_registration_payload()
        │
        └── services.py
            ├── get_service_headers()
            ├── get_user_headers()
            └── get_admin_headers()
```

## Import Dependencies

```
Services
    ↓
shared.auth           ← JWT validation
    ↓
shared.logging        ← Structured logs
    ↓
shared.testing        ← Test utilities
    ↓
Test Suite (am-tests/)
```

## Service Integration Points

### User Management Service
```python
# Imports
from shared.auth import JWTValidator
from shared.logging import initialize_logging, get_logger
from shared.testing import TokenGenerator  # For internal tests

# Initialization
initialize_logging("am-user-management")
logger = get_logger(__name__)

# Token validation in dependencies
validator = JWTValidator()
payload = validator.validate_user_token(token)
```

### Auth Tokens Service
```python
# Imports
from shared.auth import JWTValidator
from shared.logging import initialize_logging, get_logger

# Token generation and validation
validator = JWTValidator()
service_token = validator.generate_service_token(user_id)
```

### API Gateway
```python
# Imports
from shared.auth import JWTValidator
from shared.logging import LoggingMiddleware, initialize_logging

# Middleware setup
app.add_middleware(LoggingMiddleware)

# Token validation for all requests
validator = JWTValidator()
```

### Test Suite
```python
# Imports
from shared.testing import (
    TokenGenerator,
    get_user_headers,
    get_service_headers,
    create_test_user,
    get_test_client,
)

# Usage
gen = TokenGenerator()
token = gen.generate_user_token()
headers = get_user_headers()
client = await get_test_client()
```

## Data Flow

### Authentication Flow
```
Client Request
    ↓
API Gateway (validates with shared.auth)
    ↓
Service (uses same shared.auth for validation)
    ↓
Success: Process Request
Failure: 401/403 Response
```

### Logging Flow
```
Service Code
    ↓
shared.logging.logger (structured output)
    ↓
LoggingMiddleware (request context)
    ↓
JSON formatted logs to stdout/file
    ↓
Monitoring/Aggregation
```

### Testing Flow
```
Test Case
    ↓
shared.testing.TokenGenerator (create tokens)
    ↓
shared.testing.fixtures (test data)
    ↓
shared.testing.test_client (HTTP calls)
    ↓
Service Endpoint
    ↓
Assert Response
```

## Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| **DRY (Don't Repeat Yourself)** | Single `shared/` directory, no duplicates |
| **Single Responsibility** | Each module handles one concern |
| **Open/Closed** | Open for extension, closed for modification |
| **Dependency Inversion** | Services depend on abstractions (shared/) |
| **Interface Segregation** | Import only needed utilities |

## Module Dependencies Map

```
┌─────────────────────────────────────────┐
│         External Dependencies           │
│  (FastAPI, JWT, SQLAlchemy, etc.)       │
└────────────────┬────────────────────────┘
                 ↓
        ┌─────────────────┐
        │ shared/logging  │  ← Uses external logging/config
        └────────┬────────┘
                 ↓
        ┌─────────────────┐
        │  shared/auth    │  ← Uses JWT for validation
        └────────┬────────┘
                 ↓
        ┌─────────────────┐
        │ shared/testing  │  ← Uses auth & logging for tests
        └────────┬────────┘
                 ↓
        ┌─────────────────┐
        │   Services      │  ← Depend on shared modules
        └────────┬────────┘
                 ↓
        ┌─────────────────┐
        │   Test Suite    │  ← Uses testing utilities
        └─────────────────┘
```

## File Statistics

| Category | Count | Purpose |
|----------|-------|---------|
| **Auth Modules** | 2 | JWT validation & security |
| **Logging Modules** | 4 | Structured logging infrastructure |
| **Testing Utils** | 2 | Test automation tools |
| **Test Fixtures** | 2 | Pre-built test data |
| **Documentation** | 3 | Usage guides & architecture |

## Removed Duplicates

- ❌ `am/shared/` (all files consolidated to root `shared/`)
- ❌ Scattered test utilities (centralized to `shared/testing/`)
- ❌ Duplicate token generation logic (unified in `TokenGenerator`)

## Added Structure

- ✅ `shared/testing/` module (NEW)
- ✅ `shared/testing/utils/` (token_generator, test_client)
- ✅ `shared/testing/fixtures/` (users, services)
- ✅ Comprehensive documentation
- ✅ Clear import patterns

This organization ensures **zero duplication**, **maximum reusability**, and **consistent patterns** across all services! 🚀
