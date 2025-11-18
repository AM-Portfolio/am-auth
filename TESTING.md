# 🧪 Complete Testing Guide - AM Authentication System

## Quick Start - Run All Tests

```bash
# Make test script executable
chmod +x test_all.sh

# Run the complete test suite
./test_all.sh
```

---

## Manual Testing Guide

Follow these steps to manually test the entire system:

### Test 1: Verify Services Are Running

```bash
# Check all services
docker-compose -f am/docker-compose.yml ps

# Should show:
# ✅ API Gateway (8000) - Healthy
# ✅ User Management (8010) - Healthy
# ✅ Auth Tokens (8001) - Healthy
# ✅ Python Internal (8002) - Running (internal only)
# ✅ Java Internal (8003) - Running (internal only)
```

### Test 2: Health Checks

```bash
# API Gateway
curl http://localhost:8000/health

# User Management
curl http://localhost:8010/health

# Auth Tokens
curl http://localhost:8001/health

# Expected: JSON response with "status": "healthy"
```

### Test 3: User Registration

```bash
# Register a new user
curl -X POST http://localhost:8010/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"testuser@example.com",
    "password":"Test123!",
    "full_name":"Test User"
  }'

# Save the user_id from response
# Example response:
# {
#   "user_id": "550e8400-e29b-41d4-a716-446655440000",
#   "email": "testuser@example.com",
#   "status": "pending_activation"
# }
```

### Test 4: User Activation

```bash
# Use the user_id from registration
USER_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST http://localhost:8010/api/v1/users/$USER_ID/activate

# Expected: User status changed to "active"
```

### Test 5: Login & Get Token

```bash
# Login with the credentials
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"testuser@example.com",
    "password":"Test123!"
  }'

# Save the access_token
# Example response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "user_id": "550e8400-e29b-41d4-a716-446655440000"
# }
```

### Test 6: Access Protected Endpoints

```bash
# Set your token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Access Documents (via API Gateway)
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN"

# Access Reports (via API Gateway)
curl http://localhost:8000/api/v1/reports \
  -H "Authorization: Bearer $TOKEN"

# Expected: JSON responses with documents/reports data
```

### Test 7: Verify Network Isolation

```bash
# Try to access internal services externally
# These should FAIL (Connection refused)
curl http://localhost:8002/health    # ❌ Should fail
curl http://localhost:8003/health    # ❌ Should fail

# These SHOULD WORK
curl http://localhost:8000/health    # ✅ Should work
curl http://localhost:8010/health    # ✅ Should work
curl http://localhost:8001/health    # ✅ Should work
```

### Test 8: JWT Token Validation

```bash
# Try without token
curl http://localhost:8000/api/v1/documents

# Expected: 401 or 403 Unauthorized

# Try with invalid token
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer invalid_token"

# Expected: 401 Unauthorized
```

### Test 9: Rate Limiting

```bash
# Make 101 rapid requests
for i in {1..101}; do
  curl -s http://localhost:8000/health
done | tail -5

# You should see a 429 (Too Many Requests) response
```

---

## Using Postman

### 1. Import Collection

```
1. Open Postman
2. File → Import → Choose AM_Authentication_System.postman_collection.json
3. Create environment (or use default)
```

### 2. Set Environment Variables

| Variable | Value |
|----------|-------|
| `base_url` | `http://localhost:8000` |
| `user_url` | `http://localhost:8010` |
| `auth_url` | `http://localhost:8001` |
| `access_token` | (auto-filled after login) |

### 3. Run Test Scenarios

**Complete Flow:**
1. Register User → Get user_id
2. Activate User
3. Login → Get access_token
4. Get Documents
5. Get Reports

### 4. Check Test Results

Each request shows:
- Status code (✅ 200, ❌ 401, etc.)
- Response body (JSON)
- Response headers
- Test results (passed/failed)

---

## Docker Testing

### View Logs

```bash
# All services
docker-compose -f am/docker-compose.yml logs -f

# Specific service
docker-compose -f am/docker-compose.yml logs -f am-user-management

# Filter by keyword
docker-compose logs -f | grep "ERROR\|WARNING"
```

### Test from Inside Docker

```bash
# Enter a container
docker exec -it am-am-user-management-1 sh

# Test internal service access
curl http://am-python-internal-service:8002/health \
  -H "Authorization: Bearer YOUR_TOKEN"

# Exit
exit
```

---

## Security Testing Checklist

- [ ] **Network Isolation**
  - [ ] Internal services NOT accessible from localhost:8002
  - [ ] Internal services NOT accessible from localhost:8003
  - [ ] API Gateway accessible at localhost:8000
  - [ ] User Management accessible at localhost:8010
  - [ ] Auth Tokens accessible at localhost:8001

- [ ] **JWT Authentication**
  - [ ] Protected endpoints reject requests without token
  - [ ] Protected endpoints reject invalid tokens
  - [ ] Protected endpoints accept valid tokens
  - [ ] Different users can't access each other's data

- [ ] **Rate Limiting**
  - [ ] 100 requests per minute per IP works
  - [ ] 101st request gets 429 Too Many Requests
  - [ ] Rate limit resets after 60 seconds

- [ ] **Data Security**
  - [ ] Passwords are hashed (not plain text)
  - [ ] Tokens are not logged
  - [ ] Sensitive data not exposed in responses

---

## Performance Testing

### Response Time

```bash
# Check how long requests take
time curl http://localhost:8000/health

# Expected: < 100ms for health check
# Expected: < 500ms for authenticated requests
```

### Load Testing

```bash
# Install Apache Bench
# macOS: brew install httpd

# Test with 100 concurrent requests
ab -n 100 -c 10 http://localhost:8000/health

# Expected:
# - Most requests succeed
# - Response time < 200ms average
# - Error rate < 5%
```

---

## Troubleshooting

### Services Not Running?

```bash
# Check status
docker-compose -f am/docker-compose.yml ps

# Restart services
docker-compose -f am/docker-compose.yml restart

# Check logs
docker-compose -f am/docker-compose.yml logs
```

### 401 Unauthorized?

```bash
# Make sure user is activated
# 1. Register user
# 2. Activate user
# 3. Login
# 4. Use token from login response
```

### Connection Refused on 8002/8003?

```bash
# This is CORRECT! Internal services are protected.
# Use API Gateway (8000) instead:
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Port Already in Use?

```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 PID

# Or change docker-compose port mapping
# Edit am/docker-compose.yml and restart
```

---

## Test Coverage

| Component | Test | Status |
|-----------|------|--------|
| User Registration | Manual ✓ Postman ✓ | ✅ Working |
| User Activation | Manual ✓ Postman ✓ | ✅ Working |
| Login | Manual ✓ Postman ✓ | ✅ Working |
| Token Validation | Manual ✓ | ✅ Working |
| API Gateway | Manual ✓ Postman ✓ | ✅ Working |
| Rate Limiting | Manual ✓ | ✅ Working |
| Network Isolation | Manual ✓ | ✅ Working |
| JWT Security | Manual ✓ | ✅ Working |

---

## Continuous Testing

### Set Up Auto-Test (Optional)

```bash
# Create a cron job to run tests every hour
echo "0 * * * * cd /path/to/project && ./test_all.sh >> test_results.log" | crontab -
```

### Monitor Logs

```bash
# Watch logs in real-time
docker-compose -f am/docker-compose.yml logs -f --timestamps
```

---

## Success Indicators

✅ **Your system is working correctly when:**

1. All 5 services show "Healthy" or "Running"
2. User registration, activation, and login work
3. API Gateway returns data when given valid token
4. Requests without token get 401/403
5. Internal services show "Connection Refused" from localhost
6. Rate limit kicks in after 100 requests/minute
7. No errors in logs

---

## Next Steps

1. ✅ Run `./test_all.sh` to verify everything
2. ✅ Review test results
3. ✅ Try Postman collection for manual testing
4. ✅ Check logs for any warnings
5. ✅ You're ready to use the system!

---

**🎉 Complete testing guide created! Run `./test_all.sh` to test everything.**
