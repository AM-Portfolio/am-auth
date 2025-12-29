# AI Coding Agent Instructions for AM Authentication System

## Architecture Overview

This is a **microservices authentication system** with an **API Gateway pattern**. The critical architectural principle: internal services are **network isolated** and only accessible through the API Gateway.

```
Client → API Gateway (8000) → [validates user JWT] → [generates service JWT] → Internal Services
```

**Three layers of security:**
1. **Network isolation**: Internal services have no external ports
2. **User JWT**: Client authentication via `am-auth-tokens` service
3. **Service JWT**: Inter-service authentication using separate secret

## Service Port Map

| Service | Port | Exposed | Access Pattern |
|---------|------|---------|----------------|
| `am-api-gateway` | 8000 | ✅ External | All client traffic |
| `am-user-management` | 8010 | ✅ External | Registration/login only |
| `am-auth-tokens` | 8001 | ✅ External | Token operations |
| `am-python-internal-service` | 8002 | ⛔ Internal | Via Gateway only |
| `am-java-internal-service` | 8003 | ⛔ Internal | Via Gateway only |

## Critical Development Rules

### 1. Never Expose Internal Service Ports
Internal services MUST NOT have port mappings in `docker-compose.yml`. Breaking this rule defeats the security architecture.

```yaml
# ✅ CORRECT - No ports exposed
am-python-internal-service:
  # NO ports: section
  
# ❌ WRONG - Security violation
am-python-internal-service:
  ports:
    - "8002:8002"  # NEVER DO THIS
```

### 2. Two JWT Secrets Pattern
The system uses **two separate JWT secrets**:

- `JWT_SECRET` - For user tokens (client ↔ gateway)
- `INTERNAL_JWT_SECRET` - For service tokens (gateway ↔ internal services)

**Location:** Both defined in `.env.docker` and must be 32+ characters.

### 3. Service Communication Flow
**Client → Internal Service requests MUST go through this flow:**

```python
# In API Gateway endpoint (e.g., am-api-gateway/api/v1/endpoints/documents.py)
async def proxy_to_internal_service(current_user: CurrentUser = Depends(get_current_user)):
    # 1. get_current_user validates user JWT automatically
    # 2. Generate service token
    service_token = await generate_service_token(
        current_user.token,
        service_id="python-service",
        permissions=["read:documents"]
    )
    # 3. Call internal service with service token
    response = await client.get(
        f"{settings.PYTHON_SERVICE_URL}/internal/documents",
        headers={"Authorization": f"Bearer {service_token}"}
    )
```

**Never** pass user tokens directly to internal services.

## Shared Infrastructure Patterns

### Centralized Logging (`shared/logging/`)
All services use the shared logging infrastructure:

```python
# In service main.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "shared"))

from shared.logging import initialize_logging, get_logger

# Initialize once at startup
initialize_logging("am-auth-tokens")  # or "am-user-management"
logger = get_logger(__name__)

# Use throughout code
logger.info("User registered", extra={"user_id": user_id, "email": email})
```

**Log format:** JSON in production, structured in development (set via `LOG_FORMAT` env var).

### Shared JWT Utilities (`shared/auth/`)
Internal services validate tokens using `shared/auth/jwt_utils.py`:

```python
from shared.auth.jwt_utils import jwt_validator

# In FastAPI dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    token_type, payload = jwt_validator.validate_any_token(token)
    return {"type": token_type, "payload": payload}

# Use in endpoints
async def get_documents(auth_info = Depends(verify_token)):
    if auth_info["type"] == "service":
        # Service-to-service call
    elif auth_info["type"] == "user":
        # Direct user call (should be rare for internal services)
```

## FastAPI Patterns

### Dependency Injection Standard
Follow this hierarchy:

```python
# 1. Security dependency (HTTPBearer)
security = HTTPBearer()

# 2. Token verification
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validate and return payload

# 3. User/Service validation
async def validate_user_token(auth_info = Depends(verify_token)):
    if auth_info["type"] != "user":
        raise HTTPException(401)
    return auth_info["payload"]

# 4. Use in endpoints
@router.get("/documents")
async def get_documents(user_payload = Depends(validate_user_token)):
    user_id = user_payload["user_id"]
```

### Response Models
Use Pydantic models for all responses:

```python
from pydantic import BaseModel, Field

class Document(BaseModel):
    id: str = Field(..., description="Document ID")
    name: str
    size: int
    
    class Config:
        json_schema_extra = {
            "example": {"id": "123", "name": "doc.pdf", "size": 2048}
        }
```

## Development Workflow

### Starting Services
```bash
cd am
docker-compose up -d --build

# Wait 30-60s for health checks, then verify
docker-compose ps
curl http://localhost:8000/health  # API Gateway
```

### Testing Authentication Flow
```bash
# 1. Register user
curl -X POST http://localhost:8010/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# 2. Activate user (save user_id from step 1)
curl -X POST http://localhost:8010/api/v1/users/{USER_ID}/activate

# 3. Login (returns JWT token)
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# 4. Use token with API Gateway
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer {TOKEN}"
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f am-api-gateway

# Filter by keyword
docker-compose logs -f | grep "ERROR"
```

## Adding New Endpoints

### To API Gateway (for new internal service):
1. Create endpoint file: `am-api-gateway/api/v1/endpoints/new_service.py`
2. Follow pattern from `documents.py` or `reports.py`
3. Register router in `main.py`: `app.include_router(new_service.router, prefix="/api/v1", tags=["NewService"])`
4. Update root endpoint in `main.py` to list new endpoint

### To Internal Service:
Internal services should expose two endpoint types:
- `/internal/*` - Service-to-service (requires service JWT)
- `/api/v1/*` - Direct user access (requires user JWT)

## Testing

### Running Tests
```bash
cd am-user-management
pytest tests/ -v

# With coverage
pytest tests/ --cov=modules --cov-report=html
```

### Test Structure (pytest.ini)
- Unit tests: `@pytest.mark.unit`
- Integration tests: `@pytest.mark.integration`  
- API tests: `@pytest.mark.api`

### Postman Collections
Located in `postman/` directory. Import and set environment variables:
- `base_url`: http://localhost:8000
- `user_url`: http://localhost:8010
- `auth_url`: http://localhost:8001
- `access_token`: (set after login)

## Common Pitfalls

### ❌ "Can't access port 8002 from Postman"
**Correct behavior!** Internal services are not exposed. Use API Gateway (port 8000) instead.

### ❌ "401 Unauthorized" errors
- Check user is **activated** (not just registered)
- Verify token format: `Authorization: Bearer {token}` (note the space)
- Token may be expired (default: 1 hour)

### ❌ Rate limiting issues (429 errors)
- Default: 100 requests/60 seconds per IP
- Implemented in `am-api-gateway/middleware/rate_limiter.py`
- Adjust in `docker-compose.yml`: `RATE_LIMIT_REQUESTS=200`

### ❌ Service unhealthy on startup
- Java service may show unhealthy initially - wait 60s for JVM startup
- Check logs: `docker-compose logs am-java-internal-service`

## Environment Variables

**Key settings** in `.env.docker`:
- `JWT_SECRET` - User token signing (32+ chars)
- `INTERNAL_JWT_SECRET` - Service token signing (32+ chars)
- `DATABASE_URL` - PostgreSQL connection string
- `*_SERVICE_URL` - Internal Docker network URLs (use container names, not localhost)
- `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW` - Rate limiting config
- `LOG_FORMAT` - `json` (production) or `structured` (dev)

**Docker network URLs:** Use container names, not localhost:
- ✅ `http://auth-tokens:8001`
- ❌ `http://localhost:8001`

## Security Checklist for Code Reviews

- [ ] Internal services have no port mappings in `docker-compose.yml`
- [ ] Service tokens generated at API Gateway, not user tokens passed through
- [ ] JWT secrets are 32+ characters and loaded from environment
- [ ] Passwords hashed with bcrypt (never plain text)
- [ ] Input validation on all endpoints (Pydantic models)
- [ ] Rate limiting applied to public endpoints
- [ ] Sensitive data (tokens, passwords) not logged
- [ ] Database queries use SQLAlchemy ORM (not raw SQL strings)

## Documentation References

- **Architecture**: `docs/ARCHITECTURE.md` - Full system design
- **Quick Start**: `docs/QUICK_START.md` - 5-minute setup guide
- **Security**: `docs/SECURITY.md` - Security patterns and compliance
- **Postman**: `postman/QUICK_START.md` - API testing guide
- **Service READMEs**: Each service has its own README in its directory
