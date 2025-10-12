# AM Authentication & Microservices System

> **Production-ready authentication system with API Gateway pattern, microservices architecture, and centralized security.**

## 🚀 Quick Start

1. **Start all services:**
   ```bash
   cd am
   docker-compose up -d --build
   ```

2. **Verify services are running:**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health  # API Gateway
   ```

3. **Test the system:**
   - Follow [Quick Start Guide](./docs/QUICK_START.md)
   - Use [Postman Collections](./postman/README.md)

## 📁 Project Structure

```
auth-test/
├── am/
│   ├── am-api-gateway/          # API Gateway (Port 8000)
│   ├── am-user-management/      # User Service (Port 8010)
│   ├── am-auth-tokens/          # Auth Service (Port 8001)
│   ├── am-python-internal-service/   # Internal: Documents
│   └── am-java-internal-service/     # Internal: Reports
├── docs/                        # Documentation
├── postman/                     # API Testing
└── shared/                      # Shared utilities
```

## 🏗️ Architecture

```
Client → API Gateway (8000) → Internal Services
            ↓
       [Rate Limiting]
            ↓
       [JWT Validation]
            ↓
       [Service Token]
            ↓
       [Proxy Request]
```

**Key Features:**
- ✅ **Two-layer security**: Network isolation + JWT authentication
- ✅ **API Gateway pattern**: Single entry point for all requests
- ✅ **Rate limiting**: 100 requests/60 seconds per IP
- ✅ **Centralized logging**: All requests tracked
- ✅ **Service mesh**: Internal services isolated from internet

## 🎯 Services Overview

| Service | Port | Access | Purpose |
|---------|------|--------|---------|
| **API Gateway** | 8000 | ✅ Public | Single entry point, routing, auth |
| **User Management** | 8010 | ✅ Public | Registration, profiles, RBAC |
| **Auth Tokens** | 8001 | ✅ Public | JWT tokens, validation |
| **Python Service** | 8002 | ⚠️ Internal | Document processing |
| **Java Service** | 8003 | ⚠️ Internal | Report generation |

## 📚 Documentation

### Core Documentation
- **[Architecture Overview](./docs/ARCHITECTURE.md)** - System design and patterns
- **[Quick Start Guide](./docs/QUICK_START.md)** - Get up and running in 5 minutes
- **[API Gateway Guide](./am/am-api-gateway/README.md)** - API Gateway details
- **[Security Guide](./docs/SECURITY.md)** - Authentication and authorization

### Service Documentation
- [User Management Service](./am/am-user-management/README.md)
- [Auth Tokens Service](./am/am-auth-tokens/README.md)
- [API Gateway Service](./am/am-api-gateway/README.md)

### Testing & Development
- [Postman Testing Guide](./postman/README.md)
- [Development Setup](./docs/DEVELOPMENT.md)

## 🔐 Security Features

### Network Isolation
- Internal services have **no external ports**
- Only 3 services exposed to internet (vs 7 without gateway)
- **57% reduction** in attack surface

### JWT Authentication
```
User Token → API Gateway → Service Token → Internal Service
```

### Rate Limiting
- 100 requests per 60 seconds per IP
- Configurable per endpoint
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Audit Logging
- All requests logged with user context
- Response times tracked
- Security events monitored

## 🧪 Testing

### Using Postman
```bash
# Import collections from postman/ directory
1. Import User-Management-Service collection
2. Import Auth-Tokens-Service collection
3. Follow QUICK_START.md for testing flow
```

### Using cURL
```bash
# 1. Register user
curl -X POST http://localhost:8010/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# 2. Activate user (use user_id from response)
curl -X POST http://localhost:8010/api/v1/users/{USER_ID}/activate

# 3. Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# 4. Use API Gateway (use token from login)
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛠️ Development

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Java 17+ (for Java service)

### Local Development
```bash
# Start services
cd am
docker-compose up -d

# View logs
docker-compose logs -f am-api-gateway
docker-compose logs -f am-user-management

# Stop services
docker-compose down
```

### Environment Variables
See `.env.docker` for configuration:
- JWT secrets
- Database credentials
- Service URLs
- Logging configuration

## 📊 Monitoring

### Health Checks
```bash
curl http://localhost:8000/health   # API Gateway
curl http://localhost:8010/health   # User Management
curl http://localhost:8001/health   # Auth Tokens
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f am-api-gateway

# Last 100 lines
docker-compose logs --tail=100 am-api-gateway
```

## 🚢 Deployment

### Development
```bash
docker-compose up -d
```

### Production Considerations
- [ ] SSL/TLS certificates
- [ ] Distributed rate limiting (Redis)
- [ ] Load balancer in front of API Gateway
- [ ] Monitoring (Prometheus/Grafana)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Circuit breakers
- [ ] API versioning strategy

## 🎓 Key Concepts

### API Gateway Pattern
**Single entry point** for all client requests that:
- Routes requests to appropriate services
- Validates user authentication
- Generates service tokens
- Applies rate limiting
- Logs all requests

### Service Mesh
Internal services communicate via **service tokens** over Docker's internal network:
- No external port exposure
- Service-to-service authentication
- Network-level isolation

### Two-Layer Security
1. **Network Layer**: Internal services not accessible from internet
2. **Application Layer**: JWT token validation for all requests

## 🤝 Contributing

### Adding New Endpoints
1. Create endpoint file in `am/am-api-gateway/api/v1/endpoints/`
2. Follow pattern from existing endpoints
3. Register router in `main.py`
4. Update documentation
5. Add Postman tests

### Code Style
- Python: PEP 8
- FastAPI best practices
- Type hints required
- Docstrings for public methods

## 📝 Version History

### v2.0.0 (Current) - API Gateway Implementation
- ✅ API Gateway service created
- ✅ Two-layer security architecture
- ✅ Rate limiting implemented
- ✅ Centralized logging
- ✅ Service token pattern

### v1.0.0 - Initial Microservices
- User Management service
- Auth Tokens service
- Internal Python/Java services
- Direct service-to-service auth

## 🐛 Troubleshooting

### Can't access internal services from Postman
**This is correct!** Internal services (8002, 8003) are not exposed to the internet. Use the API Gateway (port 8000) instead.

### 401 Unauthorized
1. Verify user is registered and activated
2. Check token is not expired
3. Ensure token is in `Authorization: Bearer <token>` header

### 429 Rate Limit Exceeded
Wait 60 seconds or increase rate limit in `docker-compose.yml`:
```yaml
environment:
  - RATE_LIMIT_REQUESTS=200  # Increase from 100
```

### Service unhealthy
```bash
# Check logs
docker-compose logs am-java-internal-service

# Restart service
docker-compose restart am-java-internal-service
```

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: Check logs with `docker-compose logs`
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## 📜 License

Internal AM Project - Confidential

---

**Status**: ✅ Production Ready  
**Last Updated**: October 12, 2025  
**Docker Compose**: All services healthy  
**Test Coverage**: Core flows tested
