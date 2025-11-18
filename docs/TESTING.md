# Testing Guide

## 🧪 How to Test the API Gateway System

### Prerequisites
- All services must be running
- `curl` command available
- `python3` installed (for JSON formatting)

## Quick Test (2 Minutes)

```bash
# 1. Check all services are healthy
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8010/health  # User Management  
curl http://localhost:8001/health  # Auth Tokens

# 2. Get API Gateway info
curl http://localhost:8000/ | python3 -m json.tool

# 3. Try accessing protected endpoint (should fail with 401)
curl http://localhost:8000/api/v1/documents

# Expected: {"detail":"Not authenticated"}
```

## Full Test Flow

### Option 1: Using Test Script (Automated)

```bash
# Run the automated test script
cd /Users/munishm/Documents/AM-Repos/auth-test
./test-api-gateway.sh
```

The script will:
- ✅ Check all services are running
- ✅ Register a new test user
- ✅ Activate the user
- ✅ Login and get JWT token
- ✅ Test all API Gateway endpoints
- ✅ Test rate limiting
- ✅ Verify internal services are protected

### Option 2: Manual Testing with Postman

#### Step 1: Import Collections

1. Open Postman
2. Import collections from `postman/` directory:
   - `Auth-Tokens-Service.postman_collection.json`
   - `User-Management-Service.postman_collection.json`

#### Step 2: Create Environment

Create a Postman environment with these variables:

| Variable | Value |
|----------|-------|
| `base_url` | `http://localhost:8000` |
| `user_url` | `http://localhost:8010` |
| `auth_url` | `http://localhost:8001` |
| `access_token` | (will be set after login) |

#### Step 3: Test Sequence

1. **Register User**
   ```
   POST {{auth_url}}/api/v1/users/register
   Body: {
     "email": "testuser@example.com",
     "password": "SecurePass123!",
     "service_name": "testuser"
   }
   ```
   Save the `user_id` from response.

2. **Activate User**
   ```
   POST {{auth_url}}/api/v1/users/{{user_id}}/activate
   ```

3. **Login**
   ```
   POST {{auth_url}}/api/v1/auth/login
   Body: {
     "email": "testuser@example.com",
     "password": "SecurePass123!"
   }
   ```
   Save the `access_token` to environment variable.

4. **Test API Gateway Endpoints**
   ```
   GET {{base_url}}/api/v1/documents
   Headers: Authorization: Bearer {{access_token}}
   
   GET {{base_url}}/api/v1/reports
   Headers: Authorization: Bearer {{access_token}}
   
   GET {{base_url}}/api/v1/portfolio
   Headers: Authorization: Bearer {{access_token}}
   ```

### Option 3: Manual Testing with cURL

#### Step 1: Register User (Auth Service)

```bash
# Register with auth-tokens service
curl -X POST http://localhost:8001/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!",
    "service_name": "testuser"
  }'
```

Save the `user_id` from response.

#### Step 2: Activate User

```bash
# Replace {USER_ID} with actual ID
curl -X POST http://localhost:8001/api/v1/users/{USER_ID}/activate
```

#### Step 3: Login

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123!"
  }'
```

Save the `access_token` from response.

#### Step 4: Test API Gateway

```bash
# Export token for easy reuse
export TOKEN="your_access_token_here"

# Test documents endpoint
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Test reports endpoint
curl http://localhost:8000/api/v1/reports \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Test portfolio endpoint
curl http://localhost:8000/api/v1/portfolio \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Testing Rate Limiting

### Method 1: Bash Loop

```bash
# Send 105 requests to trigger rate limit
for i in {1..105}; do
  echo "Request $i"
  curl -s -w "Status: %{http_code}\n" \
    http://localhost:8000/api/v1/documents \
    -H "Authorization: Bearer $TOKEN" \
    -o /dev/null
  sleep 0.1
done
```

Expected: First 100 succeed (200), next 5 fail (429).

### Method 2: Check Headers

```bash
# View rate limit headers
curl -v http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" 2>&1 | grep -i ratelimit
```

Expected headers:
- `X-RateLimit-Limit: 100`
- `X-RateLimit-Remaining: 99`
- `X-RateLimit-Reset: 1703001234`

## Testing Security

### Test 1: Invalid Token

```bash
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer invalid_token"
```

Expected: `401 Unauthorized`

### Test 2: No Token

```bash
curl http://localhost:8000/api/v1/documents
```

Expected: `401 Unauthorized` or `403 Forbidden`

### Test 3: Internal Services Not Accessible

```bash
# These should FAIL (connection refused/timeout)
curl --connect-timeout 2 http://localhost:8002/health  # Python service
curl --connect-timeout 2 http://localhost:8003/health  # Java service
```

Expected: Connection refused (this is CORRECT - services are protected)

## Testing Password Reset Feature

### Complete Password Reset Flow

The password reset feature has three endpoints that work together:

1. **Request Reset** - User requests a password reset link
2. **Validate Token** - Verify the reset token is valid before showing form
3. **Confirm Reset** - Complete the password reset with new password

#### Step 1: Request Password Reset

```bash
curl -X POST http://localhost:8010/api/v1/request-reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "If an account exists with this email, a reset link will be sent",
  "note": "If an account exists with this email, a password reset link will be sent"
}
```

**Note:** For security, the same message is returned whether user exists or not. In development, the reset token is logged to the service logs.

#### Step 2: Get Reset Token from Logs

```bash
docker-compose logs am-user-management | grep "Reset token for" | tail -1
```

**Output example:**
```
Reset token for user@example.com: zc2XlTHE94FW9JQncusO21phwKJfWTj7JpVEApO2DGI
```

#### Step 3: Validate the Reset Token

Before allowing password reset, validate the token:

```bash
curl -X POST http://localhost:8010/api/v1/validate-reset-token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "token": "zc2XlTHE94FW9JQncusO21phwKJfWTj7JpVEApO2DGI"
  }'
```

**Success Response:**
```json
{
  "valid": true,
  "message": "Token is valid"
}
```

**Failed Response (expired/already used/revoked):**
```json
{
  "valid": false,
  "message": "Token expired"
}
```

#### Step 4: Confirm Password Reset

Once token is validated, user can set a new password:

```bash
curl -X POST http://localhost:8010/api/v1/confirm-reset \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "token": "zc2XlTHE94FW9JQncusO21phwKJfWTj7JpVEApO2DGI",
    "new_password": "NewPassword123!"
  }'
```

**Success Response:**
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

**Failed Response (invalid token/password):**
```json
{
  "success": false,
  "message": "Invalid reset token"
}
```

#### Step 5: Verify Password Changed

Login with the new password to confirm it worked:

```bash
curl -X POST http://localhost:8001/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "NewPassword123!"
  }'
```

Should return a valid JWT token.

### Password Requirements

The new password must meet these criteria:

- **Minimum 8 characters**
- **Contains uppercase letter** (A-Z)
- **Contains lowercase letter** (a-z)
- **Contains digit** (0-9)

**Examples:**
- ✅ `ValidPass123` - OK
- ✅ `MyPassword2024` - OK
- ❌ `weakpass` - No uppercase, no digit
- ❌ `NODIGITS` - No lowercase, no digit
- ❌ `short1A` - Only 7 characters

### Token Expiration

Reset tokens expire after **24 hours**. Expired tokens will return:

```json
{
  "valid": false,
  "message": "Token expired"
}
```

### Security Features

1. **One-time use**: Tokens can only be used once. Using a token marks it as used.
2. **Token revocation**: Requesting another reset revokes all previous unused tokens.
3. **Email privacy**: Same response whether user exists or not (prevents user enumeration).
4. **Token hashing**: Tokens are hashed in the database (only hash stored, not original token).
5. **Secure generation**: Tokens generated using `secrets.token_urlsafe()` with 32 bytes.

### Automated Password Reset Test

Add this to your test script:

```bash
#!/bin/bash

# Create test user
USER_ID=$(curl -s -X POST http://localhost:8010/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "resettest@example.com",
    "password": "OldPassword123!",
    "full_name": "Reset Test"
  }' | jq -r '.user_id')

# Activate user
curl -s -X PATCH http://localhost:8010/api/v1/users/$USER_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}' > /dev/null

# Request reset
curl -s -X POST http://localhost:8010/api/v1/request-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "resettest@example.com"}' > /dev/null

# Extract token from logs (wait a moment for logs)
sleep 1
TOKEN=$(docker-compose logs am-user-management | \
  grep "Reset token for resettest" | \
  tail -1 | \
  sed 's/.*: //')

# Validate token
VALID=$(curl -s -X POST http://localhost:8010/api/v1/validate-reset-token \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"resettest@example.com\",\"token\":\"$TOKEN\"}" | jq -r '.valid')

# If valid, confirm reset
if [ "$VALID" = "true" ]; then
  curl -s -X POST http://localhost:8010/api/v1/confirm-reset \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"resettest@example.com\",\"token\":\"$TOKEN\",\"new_password\":\"NewPassword123!\"}" > /dev/null
  
  # Try login with new password
  LOGIN=$(curl -s -X POST http://localhost:8001/api/v1/tokens \
    -H "Content-Type: application/json" \
    -d '{"username":"resettest@example.com","password":"NewPassword123!"}')
  
  if echo "$LOGIN" | jq -e '.access_token' > /dev/null 2>&1; then
    echo "✅ Password reset test PASSED"
  else
    echo "❌ Password reset test FAILED - Could not login with new password"
  fi
else
  echo "❌ Password reset test FAILED - Token validation failed"
fi
```

## Testing API Documentation

### Swagger UI

Open in browser:
- API Gateway: http://localhost:8000/docs
- User Management: http://localhost:8010/docs
- Auth Tokens: http://localhost:8001/docs

### ReDoc

Open in browser:
- API Gateway: http://localhost:8000/redoc
- User Management: http://localhost:8010/redoc
- Auth Tokens: http://localhost:8001/redoc

## Checking Logs

### All Services

```bash
cd am
docker-compose logs -f
```

### Specific Service

```bash
docker-compose logs -f am-api-gateway
docker-compose logs -f am-user-management
docker-compose logs -f am-auth-tokens
docker-compose logs -f am-python-internal-service
docker-compose logs -f am-java-internal-service
```

### Last N Lines

```bash
docker-compose logs --tail=100 am-api-gateway
```

### Filter for Errors

```bash
docker-compose logs am-api-gateway | grep -i error
```

## Troubleshooting

### Service Not Responding

```bash
# Check service status
docker-compose ps

# Restart service
docker-compose restart am-api-gateway

# Rebuild and restart
docker-compose up -d --build am-api-gateway

# View logs
docker-compose logs --tail=50 am-api-gateway
```

### Can't Login

1. Check user is registered:
   ```bash
   curl http://localhost:8001/api/v1/users/{USER_ID}
   ```

2. Check user is activated:
   ```bash
   # User status should be "active"
   ```

3. Check credentials are correct

4. Check auth service logs:
   ```bash
   docker-compose logs auth-tokens
   ```

### 401 Unauthorized

1. Verify token is valid:
   ```bash
   curl http://localhost:8001/api/v1/auth/validate \
     -H "Authorization: Bearer $TOKEN"
   ```

2. Check token hasn't expired

3. Ensure token is in correct format: `Bearer <token>`

### 429 Rate Limit

Wait 60 seconds or restart API Gateway to reset counters:

```bash
docker-compose restart am-api-gateway
```

## Performance Testing

### Apache Bench

```bash
# 1000 requests, 10 concurrent
ab -n 1000 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/documents
```

### k6 Load Test

```bash
# Install k6
brew install k6  # macOS

# Run load test
k6 run load-test.js
```

## Expected Test Results

### ✅ Successful Tests

- [ ] All services health checks return 200
- [ ] Can register new user
- [ ] Can activate user
- [ ] Can login and get token
- [ ] Can access documents endpoint with token
- [ ] Can access reports endpoint with token
- [ ] Invalid tokens are rejected (401)
- [ ] Rate limit headers are present
- [ ] Internal services not accessible externally
- [ ] Swagger UI loads successfully

### ⚠️ Known Issues

1. **Java service healthcheck shows unhealthy**
   - Service is actually working
   - Issue: `curl` not installed in container
   - Fix: Add `curl` to Dockerfile (optional)

2. **Rate limiting is per-container**
   - Won't work correctly with multiple API Gateway instances
   - Fix: Use Redis for distributed rate limiting (production)

## Quick Reference

### Ports

| Service | Port | Access |
|---------|------|--------|
| API Gateway | 8000 | Public |
| User Management | 8010 | Public |
| Auth Tokens | 8001 | Public |
| Python Service | 8002 | Internal Only |
| Java Service | 8003 | Internal Only |

### Test Credentials

After running test script, credentials are output at the end.

Or create your own:
- Email: `your-email@example.com`
- Password: Must meet requirements (8+ chars, upper, lower, number, special)

### Common cURL Options

```bash
# Pretty print JSON
curl ... | python3 -m json.tool

# Show headers
curl -v ...

# Show only status code
curl -w "%{http_code}\n" -o /dev/null -s ...

# Set timeout
curl --connect-timeout 5 ...
```

## Next Steps

After testing:
1. Review [Architecture Documentation](./docs/ARCHITECTURE.md)
2. Check [Security Documentation](./docs/SECURITY.md)
3. Read [Development Guide](./docs/DEVELOPMENT.md)
4. Explore [Postman Collections](./postman/README.md)

---

**Need Help?** Check the [Troubleshooting Section](#troubleshooting) or view service logs.
