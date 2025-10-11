# Service-to-Service Authentication Implementation Prompt

## Context
You are working with an existing authentication system in the `am/` directory that includes:
- **am-user-management**: Python FastAPI service (port 8000) - handles user authentication and returns access tokens
- **am-auth-tokens**: Python FastAPI service (port 8001) - manages token validation and generation
- **Shared logging infrastructure**: Centralized logging system
- **Docker Compose setup**: All services run in a Docker network

## Current State
The user authentication service successfully:
- Authenticates users and returns user details
- Issues JWT access tokens upon successful login
- Both services are currently accessible externally via ports 8000 and 8001

## Mission
Create a secure service-to-service authentication mechanism to protect internal microservices. You need to:

### 1. Create Two Demo Internal Services
Create these services in the `am/` directory to demonstrate the pattern:

#### A. `am-python-internal-service` (Python/FastAPI)
- **Port**: 8002 (internal only)
- **Purpose**: Simulate a document processing service
- **Endpoints**:
  - `GET /internal/documents` - Returns list of documents (requires auth)
  - `POST /internal/documents/process` - Process a document (requires auth)
  - `GET /health` - Health check (no auth required)

#### B. `am-java-internal-service` (Java/Spring Boot)
- **Port**: 8003 (internal only) 
- **Purpose**: Simulate a reporting service
- **Endpoints**:
  - `GET /internal/reports` - Returns list of reports (requires auth)
  - `POST /internal/reports/generate` - Generate a report (requires auth)
  - `GET /health` - Health check (no auth required)

### 2. Implement Security Architecture
Design and implement the following security layers:

#### A. Token Validation Middleware
- Create reusable JWT validation middleware for both Python and Java
- Validate tokens issued by the `am-auth-tokens` service
- Extract user context from tokens
- Handle token expiration and validation errors

#### B. Service-to-Service Authentication
- Implement internal service tokens (different from user tokens)
- Create a mechanism for services to authenticate with each other
- Use shared JWT secrets or public/private key pairs

#### C. Network Security
- Configure Docker network to prevent external access to internal services
- Only expose port 8000 (user-management) and 8001 (auth-tokens) externally
- Internal services (8002, 8003) should only be accessible within Docker network

### 3. Integration Requirements

#### A. Update Existing Services
- Modify `am-user-management` to include a new endpoint: `GET /internal/user/{user_id}` (for internal service calls)
- Add service-to-service token generation in `am-auth-tokens`
- Implement token introspection endpoint for internal services

#### B. Authentication Flow
1. **User Login**: Client → `am-user-management` → Returns user token
2. **Internal Access**: Client with user token → `am-user-management` → Internal service with validated context
3. **Service-to-Service**: Service A → `am-auth-tokens` (get service token) → Service B

### 4. Implementation Specifications

#### A. JWT Token Structure
```json
{
  "user_id": "12345",
  "username": "john_doe",
  "roles": ["user", "admin"],
  "service": "am-user-management", 
  "type": "user_token",
  "exp": 1640995200,
  "iat": 1640991600,
  "iss": "am-auth-tokens"
}
```

For service tokens:
```json
{
  "service_id": "am-python-internal-service",
  "service_name": "Document Processor",
  "type": "service_token",
  "permissions": ["read:documents", "write:documents"],
  "exp": 1640995200,
  "iat": 1640991600,
  "iss": "am-auth-tokens"
}
```

#### B. Environment Variables
Add to `.env.docker`:
```bash
# JWT Configuration for Internal Services
INTERNAL_JWT_SECRET=internal-service-super-secret-key-32chars-minimum-change-in-prod
SERVICE_TO_SERVICE_TOKEN_EXPIRY_MINUTES=60
INTERNAL_SERVICES_NETWORK_ONLY=true

# Internal Service URLs (for service discovery)
PYTHON_INTERNAL_SERVICE_URL=http://am-python-internal-service:8002
JAVA_INTERNAL_SERVICE_URL=http://am-java-internal-service:8003
```

### 5. Docker Integration
Update `docker-compose.yml` to include:
- The two new internal services (8002, 8003)
- Network configuration to restrict external access
- Health checks for all services
- Proper service dependencies

### 6. Security Middleware Implementation

#### A. Python (FastAPI) Middleware Template
```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

async def verify_internal_token(token: str = Depends(HTTPBearer())):
    try:
        payload = jwt.decode(token.credentials, INTERNAL_JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### B. Java (Spring Boot) Security Configuration Template
```java
@Configuration
@EnableWebSecurity
public class InternalServiceSecurityConfig {
    
    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter();
    }
    
    // Configure security for internal endpoints
}
```

### 7. Testing Requirements
Create test scenarios for:
- User authentication flow with access to internal services
- Service-to-service authentication
- Token validation and expiration handling
- Network security (external access blocked)
- Cross-service communication (Python ↔ Java)

### 8. Documentation
Provide:
- API documentation for all new endpoints
- Service integration guide
- Security architecture diagram
- Troubleshooting guide for common authentication issues

## Success Criteria
✅ Internal services are not directly accessible from outside Docker network
✅ User tokens can be validated by internal services  
✅ Service-to-service authentication works between Python and Java
✅ Token validation is consistent across all services
✅ Proper error handling for authentication failures
✅ Comprehensive logging for security events
✅ Integration tests demonstrate end-to-end functionality

## File Structure Expected
```
am/
├── am-user-management/          # Existing
├── am-auth-tokens/              # Existing  
├── am-python-internal-service/  # New - Python FastAPI
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── auth/
│       └── middleware.py
├── am-java-internal-service/    # New - Java Spring Boot
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/main/java/
├── docker-compose.yml           # Updated
├── .env.docker                  # Updated
└── shared/                      # Enhanced with auth utilities
    └── auth/
        ├── jwt_utils.py
        └── validation.py
```

## Implementation Priority
1. **Phase 1**: Create basic internal services with health endpoints
2. **Phase 2**: Implement JWT validation middleware for both languages
3. **Phase 3**: Configure Docker network security
4. **Phase 4**: Add service-to-service authentication
5. **Phase 5**: Integration testing and documentation

Start with Phase 1 and build incrementally, ensuring each phase works before proceeding to the next.