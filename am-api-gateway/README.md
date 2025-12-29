# API Gateway Service

## 🎯 Purpose

The API Gateway is the **single entry point** for all client requests in the AM (Asset Management) system. It provides:

- **Centralized Security**: Validates user tokens and generates service tokens
- **Request Routing**: Routes client requests to appropriate internal microservices
- **Rate Limiting**: Protects services from abuse (100 requests/60 seconds per IP)
- **Logging & Monitoring**: Tracks all requests with timing information
- **Attack Surface Reduction**: Exposes only 1 service instead of 7 to the internet

## 🏗️ Architecture

```
Clients (Postman, Browser, Mobile)
         ↓
   API Gateway (Port 8000) ✅ EXPOSED
         ↓
    [Validates User JWT]
         ↓
    [Generates Service JWT]
         ↓
   Internal Services ⚠️ NOT EXPOSED
   - Python Service (8002) - Documents
   - Java Service (8003) - Reports
   - User Management (8010) - Users
   - Auth Tokens (8001) - Tokens
```

## 📁 Project Structure

```
am-api-gateway/
├── main.py                          # FastAPI application
├── Dockerfile                       # Docker configuration
├── requirements.txt                 # Python dependencies
├── api/
│   └── v1/
│       └── endpoints/
│           ├── documents.py         # Document API (→ Python Service)
│           ├── reports.py           # Reports API (→ Java Service)
│           ├── portfolio.py         # Portfolio API (placeholder)
│           ├── trades.py            # Trades API (placeholder)
│           └── market_data.py       # Market Data API (placeholder)
├── core/
│   ├── config.py                    # Settings & configuration
│   └── auth.py                      # Authentication utilities
└── middleware/
    ├── rate_limiter.py              # Rate limiting
    └── logging_middleware.py        # Request/response logging
```

## 🔐 Security Flow

### 1. User Token Validation
```python
Authorization: Bearer <user_jwt_token>
         ↓
get_current_user() validates with auth-tokens service
         ↓
Returns CurrentUser(user_id, roles, token)
```

### 2. Service Token Generation
```python
generate_service_token(user_token, service_id, permissions)
         ↓
Calls auth-tokens service to create service token
         ↓
Returns service_jwt_token
```

### 3. Internal Service Call
```python
httpx.get(
    f"{PYTHON_SERVICE_URL}/internal/documents",
    headers={"Authorization": f"Bearer {service_token}"}
)
```

## 🚀 Endpoints

### Documents (Python Internal Service)
- `GET /api/v1/documents` - Get user documents
- `GET /api/v1/documents/all` - Get all documents (admin only)
- `GET /api/v1/documents/service-info` - Service information

### Reports (Java Internal Service)
- `GET /api/v1/reports` - Get user reports
- `GET /api/v1/reports/all` - Get all reports (admin only)
- `POST /api/v1/reports/generate` - Generate new report
- `GET /api/v1/reports/service-info` - Service information

### Portfolio (Coming Soon)
- `GET /api/v1/portfolio` - Get portfolio
- `POST /api/v1/portfolio/transaction` - Create transaction

### Trades (Coming Soon)
- `GET /api/v1/trades` - Get trades
- `POST /api/v1/trades/execute` - Execute trade

### Market Data (Coming Soon)
- `GET /api/v1/market-data/stocks/{symbol}` - Stock data
- `GET /api/v1/market-data/quotes` - Market quotes

### Health & System
- `GET /health` - Health check
- `GET /` - Welcome message with system info

## ⚙️ Configuration

Environment variables (docker-compose.yml):

```yaml
# Service URLs (internal Docker network)
AUTH_SERVICE_URL: http://auth-tokens:8001
USER_MANAGEMENT_URL: http://am-user-management:8000
PYTHON_SERVICE_URL: http://am-python-internal-service:8002
JAVA_SERVICE_URL: http://am-java-internal-service:8003

# JWT
JWT_SECRET: jwt-super-secret-signing-key-change-in-production
JWT_ALGORITHM: HS256

# Rate Limiting
RATE_LIMIT_REQUESTS: 100
RATE_LIMIT_WINDOW: 60

# Timeouts
DEFAULT_TIMEOUT: 30.0
LONG_TIMEOUT: 60.0
```

## 🧪 Testing with Postman

### 1. Register User
```
POST http://localhost:8010/api/v1/users/register
{
    "email": "test@example.com",
    "password": "Password123!",
    "full_name": "Test User"
}
```

### 2. Activate User
```
POST http://localhost:8010/api/v1/users/{user_id}/activate
```

### 3. Login
```
POST http://localhost:8001/api/v1/auth/login
{
    "email": "test@example.com",
    "password": "Password123!"
}

Response:
{
    "access_token": "eyJhbGc...",
    "token_type": "bearer"
}
```

### 4. Call API Gateway Endpoints
```
GET http://localhost:8000/api/v1/documents
Headers:
    Authorization: Bearer eyJhbGc...

GET http://localhost:8000/api/v1/reports
Headers:
    Authorization: Bearer eyJhbGc...
```

## 🛡️ Rate Limiting

- **Limit**: 100 requests per 60 seconds per IP
- **Headers Returned**:
  - `X-RateLimit-Limit: 100`
  - `X-RateLimit-Remaining: 95`
  - `X-RateLimit-Reset: 1703001234`

Response when limit exceeded:
```json
{
    "detail": "Rate limit exceeded. Try again in 45 seconds"
}
```

## 📊 Logging

All requests are logged with:
- Request method and path
- Client IP address
- User ID (if authenticated)
- Processing time
- Response status code

Headers added:
- `X-Process-Time: 0.123` (seconds)

## 🐛 Error Handling

### 401 Unauthorized
```json
{
    "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
    "detail": "Admin access required"
}
```

### 429 Too Many Requests
```json
{
    "detail": "Rate limit exceeded. Try again in 45 seconds"
}
```

### 503 Service Unavailable
```json
{
    "detail": "Document service unavailable"
}
```

## 🚢 Deployment

### Local Development
```bash
cd am-api-gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Docker
```bash
cd am
docker-compose up -d am-api-gateway
docker-compose logs -f am-api-gateway
```

## 🔍 Monitoring

### Health Check
```
GET http://localhost:8000/health

Response:
{
    "status": "healthy",
    "service": "am-api-gateway",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Service Info
```
GET http://localhost:8000/

Response:
{
    "service": "AM API Gateway",
    "version": "1.0.0",
    "endpoints": {
        "documents": "/api/v1/documents",
        "reports": "/api/v1/reports",
        "portfolio": "/api/v1/portfolio",
        "trades": "/api/v1/trades",
        "market_data": "/api/v1/market-data"
    }
}
```

## 🔒 Security Best Practices

1. **Never Expose Internal Services**: Only API Gateway has external port mapping
2. **Token Translation**: User tokens → Service tokens for internal calls
3. **Rate Limiting**: Prevents abuse and DDoS attacks
4. **Role-Based Access**: Admin endpoints check user roles
5. **Timeout Configuration**: Prevents hanging requests
6. **Audit Logging**: All requests logged for security analysis

## 🎓 Key Concepts

### Why Not Direct Access?
❌ Client → Internal Service (Bad)
- Exposes internal services to internet
- Can't add centralized security
- Multiple attack surfaces

✅ Client → API Gateway → Internal Service (Good)
- Single entry point
- Centralized auth, rate limiting, logging
- Reduced attack surface

### Service Token vs User Token
- **User Token**: Client authenticates to API Gateway
- **Service Token**: API Gateway authenticates to internal services
- **Why?**: Separation of concerns, fine-grained permissions

## 📚 Related Documentation

- [User Management Service](../am-user-management/README.md)
- [Auth Tokens Service](../am-auth-tokens/README.md)
- [Python Internal Service](../am-python-internal-service/README.md)
- [Java Internal Service](../am-java-internal-service/README.md)

## 🤝 Contributing

When adding new endpoints:
1. Create endpoint file in `api/v1/endpoints/`
2. Follow existing pattern (documents.py, reports.py)
3. Register router in `main.py`
4. Update this README
5. Test with Postman

## 📝 License

Internal AM Project - Confidential
