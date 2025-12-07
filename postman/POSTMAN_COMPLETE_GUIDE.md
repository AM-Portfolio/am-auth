# Postman Collection - Complete Testing Guide

## 📥 How to Import

### Step 1: Download the Collection
The collection file is located at:
```
postman/AM-Complete-API-Collection.postman_collection.json
```

### Step 2: Import into Postman

**Option A: Direct Import**
1. Open Postman
2. Click **File** → **Import**
3. Select **AM-Complete-API-Collection.postman_collection.json**
4. Click **Import**

**Option B: Via Postman Cloud**
1. In Postman, click **File** → **New**
2. Paste the JSON content into the import dialog

### Step 3: Create Environment (One-Time Setup)

1. Click the **Environment** icon (top right, next to settings)
2. Click **Create New Environment** or **+**
3. Name it: `Development`
4. Add variables:

| Variable | Initial Value | Type |
|----------|---------------|------|
| `base_url` | http://localhost:8000 | string |
| `user_url` | http://localhost:8010 | string |
| `auth_url` | http://localhost:8001 | string |
| `access_token` | (leave empty) | string |
| `user_id` | (leave empty) | string |

5. Click **Save**

### Step 4: Select Environment

1. Look at the top-right dropdown (currently says "No environment")
2. Click and select **Development**

---

## 🚀 Quick Start - Complete Flow

### Part 1: Register & Authenticate (5 minutes)

**Step 1:** Open the collection and navigate to **2. User Registration & Activation**

**Step 2:** Click **"Register New User"**
- ⚠️ **Important:** The email includes `{{$timestamp}}` which creates unique emails automatically
- Click **Send**
- ✅ Expected: 200/201 OK, `user_id` saved to environment automatically

**Step 3:** Click **"Activate User"**
- Uses `{{user_id}}` from environment
- Click **Send**
- ✅ Expected: 200 OK, status changed to "active"

**Step 4:** Navigate to **3. Authentication & Login** → Click **"Login - Get JWT Token"**
- ⚠️ Change email/password to match your registered user
- Click **Send**
- ✅ Expected: 200 OK, `access_token` saved automatically

**Step 5:** Click **"Validate Token"**
- Uses `{{access_token}}` from environment
- Click **Send**
- ✅ Expected: 200 OK, token is valid

---

## 📋 Collection Structure

### 1️⃣ Service Health & Info (4 requests)
Check all services are running:
- API Gateway health
- API Gateway info
- User Management health
- Auth Tokens health

**✅ Expected:** All return 200 OK

---

### 2️⃣ User Registration & Activation (3 requests)

**Register New User**
```
POST {{user_url}}/api/v1/auth/register
Body: { email, password, full_name }
Response: user_id saved to environment
```

**Activate User**
```
PATCH {{user_url}}/api/v1/users/{{user_id}}/status
Body: { status: "active" }
Response: Status changed to "active"
```

**Get User by ID**
```
GET {{user_url}}/api/v1/users/{{user_id}}
Response: User details
```

---

### 3️⃣ Authentication & Login (2 requests)

**Login - Get JWT Token**
```
POST {{auth_url}}/api/v1/tokens
Body: { username, password }
Response: access_token saved to environment
```

**Validate Token**
```
GET {{auth_url}}/api/v1/tokens/validate
Headers: Authorization: Bearer {{access_token}}
Response: Token validity and claims
```

---

### 4️⃣ Password Reset Feature (3 requests)

**Complete Password Reset Flow:**

1. **Step 1 - Request Reset**
   - Email is submitted
   - Token generated (logged to console in dev)
   - Same response for existing/non-existing users (security)

2. **Step 2 - Validate Token**
   - Get token from logs: `docker-compose logs am-user-management | grep "Reset token"`
   - Paste into request body
   - Verify token is valid

3. **Step 3 - Confirm Reset**
   - Use same token
   - Submit new password
   - Password hashed and stored
   - Token marked as used

---

### 5️⃣ API Gateway Protected Endpoints (3 requests)

These require valid JWT token (obtained from login):

**Get Documents**
```
GET {{base_url}}/api/v1/documents
Headers: Authorization: Bearer {{access_token}}
Response: Documents from internal service
```

**Get Reports**
```
GET {{base_url}}/api/v1/reports
Headers: Authorization: Bearer {{access_token}}
Response: Reports from internal service
```

**Get Portfolio**
```
GET {{base_url}}/api/v1/portfolio
Headers: Authorization: Bearer {{access_token}}
Response: Portfolio data
```

✅ **Expected:** 200 OK with data from internal services

---

### 6️⃣ Security Testing (3 requests)

These tests verify security features are working:

**No Token (Should Fail)**
- Request without Authorization header
- ❌ Expected: 403 Forbidden

**Invalid Token (Should Fail)**
- Authorization: Bearer invalid_token_12345
- ❌ Expected: 401 Unauthorized

**Malformed Auth Header (Should Fail)**
- Authorization: InvalidFormat token123
- ❌ Expected: Failure (improper format)

---

### 7️⃣ Rate Limiting Testing (2 requests)

**Single Request**
- Makes one request
- Check headers for X-RateLimit-* values

**Bulk Test - 101 Requests**
⚠️ Use Postman Runner:
1. Click **Runner** button
2. Select this request
3. Set **Iterations** to 101
4. Run

✅ **Expected:**
- Requests 1-100: 200 OK
- Request 101+: 429 Too Many Requests
- Headers show rate limit info

---

### 8️⃣ Error Scenarios (4 requests)

Test input validation:

**Invalid Email Format**
- Email: "invalid-email" (no @)
- ❌ Expected: 422 Unprocessable Entity

**Weak Password**
- Password: "weak" (too short, no requirements)
- ❌ Expected: 422 Unprocessable Entity

**Login with Wrong Password**
- Correct email, wrong password
- ❌ Expected: 401 Unauthorized

**Weak Password Reset**
- New password: "weak"
- ❌ Expected: 422 Unprocessable Entity

---

### 9️⃣ Documentation & Reference (4 links)

Quick links to Swagger/ReDoc documentation:
- API Gateway Swagger
- API Gateway ReDoc
- User Management Swagger
- Auth Tokens Swagger

Click to open in browser for interactive API docs.

---

## 🔧 Common Tasks

### Task: Complete End-to-End Test

Follow in order:
1. ✅ 1. Service Health & Info - all 4 requests
2. ✅ 2. User Registration → Register New User
3. ✅ 2. User Registration → Activate User
4. ✅ 3. Authentication → Login
5. ✅ 5. Protected Endpoints → Get Documents
6. ✅ 5. Protected Endpoints → Get Reports

**Expected Result:** All requests 200 OK ✅

---

### Task: Test Password Reset

1. ✅ Register and activate a new user
2. ✅ 4. Password Reset → Step 1 - Request Reset
3. ✅ Extract token from logs:
   ```bash
   docker-compose logs am-user-management | grep "Reset token for" | tail -1
   ```
4. ✅ 4. Password Reset → Step 2 - Validate Token (paste token)
5. ✅ 4. Password Reset → Step 3 - Confirm Reset (use same token + new password)
6. ✅ Try login with old password → should FAIL
7. ✅ Try login with new password → should SUCCEED

---

### Task: Test Security

Run all requests in **6. Security Testing**:
- No Token → ❌ Should fail
- Invalid Token → ❌ Should fail
- Malformed Header → ❌ Should fail

✅ **Expected:** All fail with appropriate error codes

---

### Task: Test Rate Limiting

1. Click on **7. Rate Limiting Testing → Bulk Test - Make 101 Requests**
2. Click **Runner** button in Postman
3. Select the request
4. Set **Iterations: 101**
5. Check **Delay (ms): 100**
6. Click **Run**

Watch console output:
- First 100: ✅ 200 OK
- Request 101+: ⚠️ 429 Too Many Requests

---

### Task: Test Error Validation

Run all requests in **8. Error Scenarios**:
1. Invalid Email Format → ❌ 422
2. Weak Password → ❌ 422
3. Wrong Password Login → ❌ 401
4. Weak Password Reset → ❌ 422

✅ All should fail with validation errors

---

## 🎯 Testing Checklist

### Health & Setup
- [ ] All 4 health checks return 200
- [ ] Environment variables set correctly
- [ ] Can access Swagger docs

### Authentication Flow
- [ ] User registration successful
- [ ] User activation successful
- [ ] Login returns JWT token
- [ ] Token saved to environment
- [ ] Token validation successful

### Protected Endpoints
- [ ] Get Documents returns 200
- [ ] Get Reports returns 200
- [ ] Get Portfolio returns 200
- [ ] All use correct token from environment

### Password Reset
- [ ] Request reset returns success
- [ ] Token extracted from logs
- [ ] Token validation successful
- [ ] Password reset completes
- [ ] Old password rejected
- [ ] New password accepted

### Security
- [ ] No token → 403
- [ ] Invalid token → 401
- [ ] Malformed header → Fails appropriately

### Error Handling
- [ ] Invalid email → 422
- [ ] Weak password → 422
- [ ] Wrong password login → 401
- [ ] Clear error messages returned

### Rate Limiting
- [ ] Requests 1-100: 200 OK
- [ ] Request 101+: 429 Too Many Requests
- [ ] Rate limit headers present

---

## 🐛 Troubleshooting

### Issue: "Cannot GET /health"
**Problem:** Services not running
**Solution:**
```bash
cd am
docker-compose up -d --build
docker-compose ps  # Verify all running
```

### Issue: "401 Unauthorized" on protected endpoints
**Problem:** Token not set or invalid
**Solution:**
1. Run Login request again
2. Check access_token in environment
3. Verify "Authorization" header uses "Bearer " prefix

### Issue: User already exists error
**Problem:** Email address reused
**Solution:**
- Registration request uses `{{$timestamp}}` which auto-generates unique emails
- If manual email: use different email each time
- Example: testuser+123@example.com

### Issue: "PATCH /users/{id}/status" returns 404
**Problem:** {{user_id}} not set in environment
**Solution:**
1. Run "Register New User" first
2. Check it saves user_id automatically
3. Verify in environment variables

### Issue: Cannot find Reset token
**Problem:** Token not logged to console
**Solution:**
```bash
# Check service logs directly
docker-compose logs am-user-management | grep "Reset token"

# Watch logs in real-time
docker-compose logs -f am-user-management
```

### Issue: Rate limit test shows all 200
**Problem:** Limit configured higher than 100
**Solution:**
Check docker-compose.yml:
```yaml
RATE_LIMIT_REQUESTS=100  # Should be 100
RATE_LIMIT_WINDOW=60     # 60 seconds
```

---

## 📖 Tips & Tricks

### 💡 Auto-Generate Unique Emails
Use `{{$timestamp}}` in email field:
```json
{
  "email": "testuser{{$timestamp}}@example.com"
}
```
This creates: `testuser1700000000000@example.com`

### 💡 Save Token to Environment
Click on a response, then:
```javascript
var jsonData = pm.response.json();
pm.environment.set("access_token", jsonData.access_token);
```
Already configured in "Login" request ✅

### 💡 Pretty Print JSON Response
After sending request, click **Pretty** tab to format JSON nicely

### 💡 Copy Token from Response
1. Send Login request
2. Select access_token value in response
3. Copy with Cmd+C
4. Paste in Authorization header

### 💡 View Request/Response Details
- **Headers tab:** See what was sent
- **Body tab:** See request payload
- **Pre-request Script:** Auto-run before each request
- **Tests tab:** Auto-validate responses

### 💡 Batch Run Multiple Requests
1. Select multiple requests (Cmd+click)
2. Click **Runner**
3. Check "Run all requests in collection"
4. Run and view results

---

## 🔒 Security Notes

⚠️ **Important for Production:**
- Never hardcode credentials in collection
- Use environment variables for secrets
- Don't commit tokens to version control
- Use separate environments for prod/dev
- Regenerate tokens regularly
- Use environment-specific collections

---

## 📞 Support

### Issues?
1. Check **TESTING.md** in docs/ directory
2. Review service logs: `docker-compose logs -f`
3. Verify all services running: `docker-compose ps`
4. Restart services: `docker-compose down && docker-compose up -d --build`

### Documentation
- **Quick Start:** docs/QUICK_START.md
- **Testing Guide:** docs/TESTING.md
- **API Documentation:** http://localhost:8000/docs (Swagger)

---

## ✅ You're Ready!

1. ✅ Import the collection
2. ✅ Create the environment
3. ✅ Start the services
4. ✅ Run the tests

**Happy Testing! 🚀**
