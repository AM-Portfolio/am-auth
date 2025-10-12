# API Gateway Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Build and Start All Services
```bash
cd am
docker-compose up -d --build
```

### 2. Check Service Health
```bash
# Check all services are running
docker-compose ps

# Check API Gateway logs
docker-compose logs -f am-api-gateway

# Check health endpoints
curl http://localhost:8000/health
curl http://localhost:8010/health
curl http://localhost:8001/health
```

### 3. Test Complete Flow

#### Step 1: Register User
```bash
curl -X POST http://localhost:8010/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "Password123!",
    "full_name": "Test User"
  }'
```

Response:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "testuser@example.com",
  "full_name": "Test User",
  "status": "pending_activation"
}
```

#### Step 2: Activate User
```bash
curl -X POST http://localhost:8010/api/v1/users/550e8400-e29b-41d4-a716-446655440000/activate
```

#### Step 3: Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "Password123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Step 4: Test API Gateway Endpoints

**Get Documents (via API Gateway):**
```bash
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Get Reports (via API Gateway):**
```bash
curl http://localhost:8000/api/v1/reports \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Test Rate Limiting:**
```bash
# Make 101 requests quickly to trigger rate limit
for i in {1..101}; do
  curl http://localhost:8000/api/v1/documents \
    -H "Authorization: Bearer YOUR_TOKEN_HERE"
done
```

## 🎯 Port Mapping

| Service | External Port | Internal Port | Access |
|---------|--------------|---------------|--------|
| API Gateway | 8000 | 8000 | ✅ PUBLIC |
| User Management | 8010 | 8000 | ✅ PUBLIC (for user registration/login) |
| Auth Tokens | 8001 | 8001 | ✅ PUBLIC (for token operations) |
| Python Internal | - | 8002 | ⚠️ INTERNAL ONLY |
| Java Internal | - | 8003 | ⚠️ INTERNAL ONLY |

## 🔍 Debugging

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f am-api-gateway
docker-compose logs -f am-user-management
docker-compose logs -f am-python-internal-service
docker-compose logs -f am-java-internal-service
```

### Test Internal Services (from inside Docker)
```bash
# Get a shell inside API Gateway
docker exec -it am-am-api-gateway-1 bash

# Test internal service
curl http://am-python-internal-service:8002/health
curl http://am-java-internal-service:8003/health
```

### Common Issues

**Issue**: Can't access internal services from Postman
**Solution**: This is by design! Use API Gateway (port 8000) instead

**Issue**: 401 Unauthorized
**Solution**: Make sure you:
1. Registered user
2. Activated user
3. Logged in and got token
4. Using token in Authorization header

**Issue**: 429 Rate Limit Exceeded
**Solution**: Wait 60 seconds or increase rate limit in docker-compose.yml

**Issue**: 503 Service Unavailable
**Solution**: Check if internal services are running:
```bash
docker-compose ps
docker-compose logs am-python-internal-service
docker-compose logs am-java-internal-service
```

## 📊 Test Results Checklist

- [ ] All services start successfully
- [ ] Can register user at port 8010
- [ ] Can activate user
- [ ] Can login and get JWT token
- [ ] Can access documents via API Gateway (8000)
- [ ] Can access reports via API Gateway (8000)
- [ ] Rate limiting works (429 after 100 requests)
- [ ] Cannot access internal services from Postman (connection refused)
- [ ] Logs show service token generation
- [ ] Health checks all return 200 OK

## 🎓 Architecture Verification

### ✅ What Should Work
- Client → API Gateway (8000) → Internal Services
- API Gateway validates user token
- API Gateway generates service token
- Internal services validate service token

### ❌ What Should NOT Work
- Client → Internal Service directly (no port mapping)
- Using user token with internal services (wrong token type)

## 📝 Next Steps

1. Test all endpoints with Postman
2. Verify rate limiting behavior
3. Check logs for service token generation
4. Try accessing internal services directly (should fail)
5. Monitor performance under load
6. Add more endpoints as needed

## 🔒 Security Validation

- [ ] Internal services not accessible from host machine
- [ ] Rate limiting prevents abuse
- [ ] Service tokens used for internal calls
- [ ] All requests logged with user context
- [ ] Admin endpoints check roles properly

---

**Need Help?** Check the main README.md or docker-compose logs
