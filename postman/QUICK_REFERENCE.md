# Postman Quick Reference Card

## 🚀 30-Second Setup

1. **Import Collection**
   - File → Import → Select `AM-Complete-API-Collection.postman_collection.json`

2. **Create Environment**
   - Click Environment icon (top right)
   - Create New: `Development`
   - Add 5 variables (see below)

3. **Select Environment**
   - Top-right dropdown → Select `Development`

4. **Start Testing**
   - Open collection and follow the flows

---

## 📋 Environment Variables

Create these in your `Development` environment:

```
base_url        = http://localhost:8000
user_url        = http://localhost:8010
auth_url        = http://localhost:8001
access_token    = (leave empty, auto-filled)
user_id         = (leave empty, auto-filled)
```

---

## 🔄 Complete Test Flow (10 minutes)

```
1. Health Checks
   ↓ (verify all services running)
2. Register User
   ↓ (saves user_id)
3. Activate User
   ↓ (status → active)
4. Login
   ↓ (saves access_token)
5. Get Protected Endpoint
   ↓ (uses access_token)
   
✅ Result: All 200 OK
```

---

## 🔐 Password Reset Test (15 minutes)

```
1. Request Reset
   ↓ (check logs for token)
2. Copy Token
   $ docker-compose logs am-user-management | grep "Reset token"
   ↓
3. Validate Token
   ↓ (paste token)
4. Confirm Reset
   ↓ (use same token)
5. Try Old Password
   ↓ ❌ Should fail
6. Try New Password
   ↓ ✅ Should work
   
✅ Result: Password changed
```

---

## 📦 What's Included

### 9 Test Groups
1. **Service Health & Info** (4 requests)
2. **User Registration & Activation** (3 requests)
3. **Authentication & Login** (2 requests)
4. **Password Reset Feature** (3 requests)
5. **API Gateway Protected Endpoints** (3 requests)
6. **Security Testing** (3 requests)
7. **Rate Limiting Testing** (2 requests)
8. **Error Scenarios** (4 requests)
9. **Documentation & Reference** (4 links)

**Total: 27 requests + 4 documentation links**

---

## ✅ Expected Results

| Group | Result | Details |
|-------|--------|---------|
| Health | ✅ All 200 | Services running |
| Registration | ✅ 200/201 | User created |
| Activation | ✅ 200 | Status changed |
| Login | ✅ 200 | Token issued |
| Protected | ✅ 200 | Data returned |
| Security | ✅ All fail | Auth required |
| Rate Limit | ✅ 100 OK, 1 fail | 429 on 101st |
| Errors | ✅ All fail | 422/401 errors |

---

## 🎯 Common Tasks

### "I want to register and test"
1. Go to **2. User Registration & Activation**
2. Click **Register New User** → Send
3. Click **Activate User** → Send
4. Go to **3. Authentication & Login**
5. Click **Login - Get JWT Token** → Send
6. Go to **5. API Gateway Protected Endpoints**
7. Click any endpoint → Send

✅ All should return 200

---

### "I want to test password reset"
1. Go to **4. Password Reset Feature**
2. Click **Step 1 - Request Password Reset** → Send
3. In terminal: `docker-compose logs am-user-management | grep "Reset token"`
4. Copy the token (starts with letter, 43 chars)
5. Go to **Step 2 - Validate Reset Token**
6. Paste token in body → Send
7. Go to **Step 3 - Confirm Password Reset**
8. Paste token + enter new password → Send

✅ All should succeed

---

### "I want to test security"
1. Go to **6. Security Testing**
2. Run all 3 requests
3. Verify all FAIL (401/403)

✅ Security working correctly

---

### "I want to test error handling"
1. Go to **8. Error Scenarios**
2. Run all 4 requests
3. Verify all return 422/401

✅ Validation working

---

### "I want to test rate limiting"
1. Go to **7. Rate Limiting Testing**
2. Click **Bulk Test - Make 101 Requests**
3. Click Runner button
4. Set Iterations: 101
5. Click Run

✅ Watch first 100 succeed, 101st fail

---

## 🔑 Key Variables

After each major step:

| Step | Auto-Saved To | Value |
|------|---------------|-------|
| Register | `user_id` | UUID of created user |
| Login | `access_token` | JWT token (30 min valid) |

These auto-populate in requests using `{{variable_name}}`

---

## 📌 Useful Endpoints

### Quick Reference
```
API Gateway:    http://localhost:8000
User Management: http://localhost:8010
Auth Tokens:    http://localhost:8001
Swagger Docs:   http://localhost:8000/docs
```

### Most Used Requests
- Register: `POST /api/v1/auth/register`
- Activate: `PATCH /api/v1/users/{id}/status`
- Login: `POST /api/v1/tokens`
- Protected: `GET /api/v1/documents` (+ token)

---

## ⚡ Pro Tips

### 💡 Auto-increment for unique emails
Use `{{$timestamp}}` in email:
```
testuser{{$timestamp}}@example.com
```

### 💡 View rate limit status
Check headers in response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1234567890
```

### 💡 Debug requests
- Click **Pre-request Script** tab → see setup logic
- Click **Tests** tab → see validation logic
- Click **Response** → see details

### 💡 Batch run
- Collection menu → **Run collection**
- Or Runner button (top left)

### 💡 Compare responses
- Send request 1
- Send request 2
- Click timeline/compare to see diff

---

## 🚨 Troubleshooting

### Services not responding?
```bash
docker-compose ps          # Check status
docker-compose logs -f     # Watch logs
```

### Token not saving?
1. Verify login request succeeded
2. Check access_token in environment
3. Re-send login request

### Can't find reset token?
```bash
docker-compose logs am-user-management | grep "Reset token"
```

### Rate limit not triggering?
- Make sure you're running 101+ requests
- Check delay is reasonable (100ms)
- Verify RATE_LIMIT_REQUESTS=100 in docker-compose.yml

---

## 📊 Test Execution Times

| Test | Time |
|------|------|
| Health check | ~50ms |
| Register user | ~100ms |
| Login | ~150ms |
| Protected endpoint | ~100ms |
| Password reset flow | ~300ms |
| Rate limit (101 requests) | ~10s |

---

## ✨ Collection Features

✅ **Auto-saving variables**
- user_id after registration
- access_token after login

✅ **Pre-configured requests**
- All 27 requests ready to use
- Environment variables pre-populated
- Examples included

✅ **Test scripts**
- Auto-validate responses
- Clear error messages
- Save important values

✅ **Documentation**
- Inline request descriptions
- Expected responses
- Error scenarios

---

## 📚 Related Documentation

- **Full Guide:** `postman/POSTMAN_COMPLETE_GUIDE.md`
- **Testing Guide:** `docs/TESTING.md`
- **Quick Start:** `docs/QUICK_START.md`
- **API Docs (Live):** http://localhost:8000/docs

---

## 🎉 Ready to Test?

1. ✅ Import collection
2. ✅ Create environment
3. ✅ Select environment
4. ✅ Start services: `docker-compose up -d --build`
5. ✅ Run tests

**Have fun! 🚀**
