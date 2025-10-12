# Quick Start Guide

## Get Started in 5 Minutes! 🚀

### Prerequisites
- Docker & Docker Compose installed
- Postman (optional, for API testing)

### Step 1: Start All Services

```bash
cd am
docker-compose up -d --build
```

Wait 30-60 seconds for all services to start.

### Step 2: Verify Services

```bash
# Check all services are running
docker-compose ps

# Should show:
# - am-api-gateway (port 8000) - HEALTHY
# - am-user-management (port 8010) - HEALTHY
# - am-auth-tokens (port 8001) - HEALTHY
# - am-python-internal-service - HEALTHY
# - am-java-internal-service - (may show unhealthy but is functional)
```

### Step 3: Test API Gateway

```bash
# Check API Gateway health
curl http://localhost:8000/health

# Get service info
curl http://localhost:8000/
```

Expected response:
```json
{
  "service": "AM API Gateway",
  "version": "1.0.0",
  "endpoints": {
    "documents": "/api/v1/documents",
    "reports": "/api/v1/reports",
    ...
  }
}
```

### Step 4: Register a User

```bash
curl -X POST http://localhost:8010/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

**Save the `user_id` from the response!**

Example response:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "testuser@example.com",
  "status": "pending_activation"
}
```

### Step 5: Activate User

```bash
# Replace {USER_ID} with the ID from step 4
curl -X POST http://localhost:8010/api/v1/users/550e8400-e29b-41d4-a716-446655440000/activate
```

Response:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active"
}
```

### Step 6: Login and Get Token

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!"
  }'
```

**Save the `access_token` from the response!**

Example response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Step 7: Call API Gateway Endpoints

Now use your token to access the API Gateway:

**Get Documents:**
```bash
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Get Reports:**
```bash
curl http://localhost:8000/api/v1/reports \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Get Portfolio (placeholder):**
```bash
curl http://localhost:8000/api/v1/portfolio \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Expected responses show data from internal services!

### Step 8: Test Rate Limiting (Optional)

```bash
# Make 101 requests to trigger rate limit
for i in {1..101}; do
  echo "Request $i"
  curl -s http://localhost:8000/api/v1/documents \
    -H "Authorization: Bearer YOUR_TOKEN_HERE" \
    -w "Status: %{http_code}\n" \
    -o /dev/null
done
```

After 100 requests, you should see **429 Too Many Requests**.

### Step 9: Verify Security (Optional)

Try to access internal services directly (this should FAIL):

```bash
# These should not work (connection refused or timeout)
curl http://localhost:8002/health  # Python service - SHOULD FAIL
curl http://localhost:8003/health  # Java service - SHOULD FAIL
```

This is **correct behavior** - internal services are not exposed!

## 🎉 Success!

You've successfully:
- ✅ Started all microservices
- ✅ Registered and activated a user
- ✅ Logged in and obtained JWT token
- ✅ Called API Gateway endpoints
- ✅ Verified internal services are protected

## 📊 Port Reference

| Service | Port | Access | URL |
|---------|------|--------|-----|
| API Gateway | 8000 | Public | http://localhost:8000 |
| User Management | 8010 | Public | http://localhost:8010 |
| Auth Tokens | 8001 | Public | http://localhost:8001 |
| Python Service | 8002 | Internal Only | ⛔ Not accessible |
| Java Service | 8003 | Internal Only | ⛔ Not accessible |

## 🧪 Using Postman

1. Import collections from `postman/` directory:
   - `User-Management-Service.postman_collection.json`
   - `Auth-Tokens-Service.postman_collection.json`

2. Create environment with:
   - `base_url`: `http://localhost:8000`
   - `user_url`: `http://localhost:8010`
   - `auth_url`: `http://localhost:8001`
   - `access_token`: (set after login)

3. Follow the testing sequence:
   - Register User
   - Activate User
   - Login
   - Get Documents
   - Get Reports

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs -f

# Restart all services
docker-compose down
docker-compose up -d --build
```

### Can't login
- Verify user is activated (Step 5)
- Check email and password are correct
- Try registering a new user

### 401 Unauthorized
- Token may be expired (login again)
- Check Authorization header format: `Bearer <token>`
- Verify token is copied correctly (no extra spaces)

### 429 Rate Limit Exceeded
- Wait 60 seconds
- Or increase limit in `docker-compose.yml`:
  ```yaml
  environment:
    - RATE_LIMIT_REQUESTS=200
  ```

### Can't access port 8002 or 8003
- **This is correct!** Internal services are not exposed
- Use API Gateway (port 8000) instead

## 📚 Next Steps

- Read [Architecture Documentation](./ARCHITECTURE.md)
- Explore [API Gateway Details](../am/am-api-gateway/README.md)
- Learn about [Security Architecture](./SECURITY.md)
- Review [Development Guide](./DEVELOPMENT.md)

## 🔍 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f am-api-gateway
docker-compose logs -f am-user-management

# Last 50 lines
docker-compose logs --tail=50 am-api-gateway
```

### Check Health
```bash
# Quick health check script
curl -s http://localhost:8000/health && echo " ✅ API Gateway"
curl -s http://localhost:8010/health && echo " ✅ User Management"
curl -s http://localhost:8001/health && echo " ✅ Auth Tokens"
```

## 💡 Pro Tips

1. **Save your token**: Export it as an environment variable
   ```bash
   export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   curl http://localhost:8000/api/v1/documents -H "Authorization: Bearer $TOKEN"
   ```

2. **Pretty print JSON**: Use `jq` or `python -m json.tool`
   ```bash
   curl http://localhost:8000/api/v1/documents \
     -H "Authorization: Bearer $TOKEN" | jq
   ```

3. **Check rate limits**: Look at response headers
   ```bash
   curl -v http://localhost:8000/api/v1/documents \
     -H "Authorization: Bearer $TOKEN" 2>&1 | grep -i ratelimit
   ```

---

**Happy Testing! 🎉**

If you encounter any issues, check the logs or refer to the [Troubleshooting Guide](./TROUBLESHOOTING.md).
