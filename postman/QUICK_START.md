# Postman Quick Start Guide

## 🚀 Import Collections (30 seconds)

1. Open Postman
2. Drag `Auth-Tokens-Service.postman_collection.json` into Postman
3. Drag `User-Management-Service.postman_collection.json` into Postman
4. Done! ✅

## ⚡ Quick Test Flows

### Test Google OAuth (Automated - 3 clicks)

**In Auth Tokens Collection → "Complete Google OAuth Flow (Test)":**

1. Click ▶️ **Step 1: Generate Mock Google Token**
2. Click ▶️ **Step 2: Authenticate with Google**  
3. Click ▶️ **Step 3: Validate Internal JWT**

✅ **Result:** Complete OAuth flow tested, JWT token ready to use!

### Test Service Registration (Automated - 2 clicks)

**In User Management Collection → "Complete Service Registration Flow":**

1. Click ▶️ **Step 1: Register Service**
2. Click ▶️ **Step 2: Validate Credentials**

✅ **Result:** OAuth app registered, credentials validated!

## 📋 Manual Testing

### Create User & Login
```
1. User Management → User Authentication → Register New User
2. User Management → User Authentication → Login
3. Auth Tokens → Traditional Authentication → Create Token
```

### Google User Flow
```
1. Auth Tokens → Testing → Generate Mock Google Token
2. Auth Tokens → Google OAuth → Authenticate with Google Token
3. Auth Tokens → Traditional Authentication → Validate Token
```

## 🔑 Key Endpoints

### Most Used
- `POST /api/v1/tokens` - Get JWT token
- `POST /api/v1/auth/google/token` - Google OAuth
- `POST /api/v1/service/register` - Register OAuth app
- `POST /api/v1/auth/register` - Create user

### Health Checks
- `GET localhost:8080/health` - Auth service
- `GET localhost:8000/health` - User service

## 💡 Pro Tips

1. **Auto-save:** All tokens/credentials save automatically to variables
2. **Console:** View → Show Postman Console for detailed logs
3. **Workflows:** Use numbered "Step" folders for guided testing
4. **Variables:** Check variables tab to see saved credentials

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Token expired - regenerate with login |
| Invalid scope | Use: `profile:read`, `data:read`, `data:write`, `admin:full` |
| Login fails | Use `email` field (not `username`) |
| Google OAuth mock fails | Known issue - use real Google credentials for production |

## 📁 Collection Structure

**Auth Tokens (9 endpoints):**
- Health & Info (3)
- Traditional Auth (3)
- Google OAuth (1)
- Testing (2)

**User Management (14 endpoints):**
- Health & Info (3)
- User Auth (2)
- Google OAuth (2)
- Service Registration (4)
- Internal APIs (1)
- Automated Flows (2)

## 🎯 Test Everything (5 minutes)

1. Run all health checks
2. Register new user
3. Test Google OAuth flow (automated)
4. Register service (automated)
5. Validate all tokens

**You're ready to test! 🚀**

---

For detailed docs, see `README.md` and `ENDPOINT_TEST_RESULTS.md`
