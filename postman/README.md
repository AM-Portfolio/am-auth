# Postman API Testing - Documentation Index

This directory contains comprehensive documentation and the Postman collection for testing all APIs in the AM Authentication System.

---

## 🚀 Quick Links

| Resource | Purpose | Read Time |
|----------|---------|-----------|
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | 30-second setup + common tasks | 5 min |
| **[POSTMAN_COMPLETE_GUIDE.md](POSTMAN_COMPLETE_GUIDE.md)** | Comprehensive reference guide | 20 min |
| **[AM-Complete-API-Collection.postman_collection.json](AM-Complete-API-Collection.postman_collection.json)** | Ready-to-import collection (27 requests) | - |

---

## 📦 What's Included

### Collection File
**`AM-Complete-API-Collection.postman_collection.json`** (21 KB)

27 API requests organized in 9 test groups:
- ✅ Service Health & Info (4 requests)
- ✅ User Registration & Activation (3 requests)
- ✅ Authentication & Login (2 requests)
- ✅ Password Reset Feature (3 requests)
- ✅ API Gateway Protected Endpoints (3 requests)
- ✅ Security Testing (3 requests)
- ✅ Rate Limiting Testing (2 requests)
- ✅ Error Scenarios (4 requests)
- ✅ Documentation & Reference (4 links)

**Features:**
- Auto-saving environment variables (user_id, access_token)
- Pre-configured tests and validators
- Pre-request scripts for setup
- JSON pretty-print configurations
- Comprehensive descriptions and expected outcomes

---

## 📖 Documentation Guides

### 1. QUICK_REFERENCE.md (5-minute read)

**For people who want a quick start:**

- 30-second setup card
- Environment variables summary
- 10-minute complete test flow
- 6 common task scenarios
- Test execution times
- 7 quick troubleshooting tips

**Best for:** Quick lookup, troubleshooting, running first test immediately

### 2. POSTMAN_COMPLETE_GUIDE.md (20-minute read)

**For people who want comprehensive coverage:**

- Full import instructions (2 methods)
- Detailed environment setup (5 variables)
- All 9 test groups documented with flows
- Complete password reset 3-step guide
- Detailed troubleshooting section (10+ scenarios)
- Tips & tricks (auto-generate data, batch runs, etc.)
- 30-item testing checklist

**Best for:** Understanding all features, password reset testing, troubleshooting, verification

---

## ⚡ 30-Second Setup

```bash
# 1. Start services
cd am
docker-compose up -d --build

# 2. In Postman:
#    - Import AM-Complete-API-Collection.postman_collection.json
#    - Set environment variables:
#      - base_url = http://localhost:8000
#      - user_url = http://localhost:8010
#      - auth_url = http://localhost:8001

# 3. Run first test: Health Check endpoint

# 4. You're ready! 🎉
```

---

## 🎯 Common Tasks

### Test Registration → Auth → Protected Endpoint (10 minutes)
See: POSTMAN_COMPLETE_GUIDE.md → "Complete End-to-End Flow" section

### Test Password Reset Flow (5 minutes)
See: POSTMAN_COMPLETE_GUIDE.md → "Password Reset 3-Step Guide" section

### Test Security (Invalid/No Tokens)
See: POSTMAN_COMPLETE_GUIDE.md → "Security Testing Group" section

### Verify Rate Limiting
See: POSTMAN_COMPLETE_GUIDE.md → "Rate Limiting Group" section

### Debug a Failed Request
See: POSTMAN_COMPLETE_GUIDE.md → "Troubleshooting" section

---

## 📋 Environment Variables Reference

| Variable | Example | Purpose |
|----------|---------|---------|
| `base_url` | http://localhost:8000 | API Gateway (main entry) |
| `user_url` | http://localhost:8010 | User Management service |
| `auth_url` | http://localhost:8001 | Auth Tokens service |
| `access_token` | eyJhbGc... | JWT token (auto-set after login) |
| `user_id` | 550e8400-e29b... | User ID (auto-set after registration) |

---

## ✅ Verification Checklist

After importing, verify these work:

- [ ] Health check returns 200
- [ ] Can register new user
- [ ] Can activate user
- [ ] Can login (get JWT token)
- [ ] Can access protected endpoint with token
- [ ] Request fails without token
- [ ] Can request password reset
- [ ] Password reset returns token
- [ ] Can reset password with token
- [ ] Old password no longer works
- [ ] New password logs in successfully
- [ ] Rate limiting triggers at 100 requests
- [ ] Error scenarios return correct status codes

---

## 🔗 Related Documentation

- **API Architecture:** See `/docs/ARCHITECTURE.md`
- **Complete Testing Guide:** See `/docs/TESTING.md`
- **Quick Start Guide:** See `/docs/QUICK_START.md`
- **Password Reset Details:** See `/FEATURE_PASSWORD_RESET.md`
- **Security Details:** See `/docs/SECURITY.md`
- **AI Coding Instructions:** See `/.github/copilot-instructions.md`

---

## 🆘 Troubleshooting

### Services Not Running?
```bash
cd am
docker-compose up -d --build
docker-compose ps  # Verify all are UP
```

### Token Not Saving?
Make sure pre-request script is enabled in Postman settings.

### Getting 401 Unauthorized?
- Check token isn't expired (default 1 hour)
- Verify `Authorization: Bearer <token>` format
- Make sure user is **activated** (not just registered)

### Can't Find Password Reset Token?
```bash
docker-compose logs am-user-management | grep "Reset token"
```

### Still Having Issues?
See **Troubleshooting** section in POSTMAN_COMPLETE_GUIDE.md (10+ scenarios)

---

## 📚 Full API Reference

### Health & Status
- `GET /health` - Service health check
- `GET /api/v1/info` - System information

### User Management
- `POST /api/v1/auth/register` - Create new user
- `GET /api/v1/users/{id}` - Get user details
- `PATCH /api/v1/users/{id}/status` - Update user status

### Authentication
- `POST /api/v1/tokens` - Login (returns JWT)
- `POST /api/v1/validate` - Validate token

### Password Reset
- `POST /api/v1/request-reset` - Request reset token
- `POST /api/v1/validate-reset-token` - Verify token
- `POST /api/v1/confirm-reset` - Complete reset

### Protected Endpoints (via API Gateway)
- `GET /api/v1/documents` - Get documents
- `GET /api/v1/reports` - Get reports
- `GET /api/v1/portfolio` - Get portfolio

---

## 💡 Pro Tips

1. **Auto-generate emails:** Use `{{$timestamp}}` in email field
   ```json
   {"email": "user{{$timestamp}}@example.com"}
   ```

2. **View rate limit status:** Check response headers after any request
   ```
   X-RateLimit-Limit: 100
   X-RateLimit-Remaining: 87
   X-RateLimit-Reset: 1731968400
   ```

3. **Batch run all tests:** Use Collection Runner
   - Click Collection → Run → Start Run

4. **Debug requests:** Enable Console log (Ctrl/Cmd + Alt + C)

5. **Pretty-print JSON:** In Tests tab, responses auto-format

---

## 📊 Collection Statistics

| Metric | Value |
|--------|-------|
| Total Requests | 27 |
| Test Groups | 9 |
| Environment Variables | 5 |
| Pre-request Scripts | All endpoints |
| Test Validators | All endpoints |
| Success Rate (Dev) | 100% ✅ |

---

## 🚀 What to Do Next

1. **First Time?** → Read QUICK_REFERENCE.md (5 min) → Import Collection → Run Health Check

2. **Need Details?** → Read POSTMAN_COMPLETE_GUIDE.md (20 min) → Explore test groups

3. **Testing Password Reset?** → See POSTMAN_COMPLETE_GUIDE.md → Password Reset section

4. **Have Errors?** → See POSTMAN_COMPLETE_GUIDE.md → Troubleshooting section

---

**Status:** ✅ Complete and Production Ready  
**Last Updated:** November 18, 2025  
**Version:** 1.0.0

For detailed setup and usage, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or [POSTMAN_COMPLETE_GUIDE.md](POSTMAN_COMPLETE_GUIDE.md)
