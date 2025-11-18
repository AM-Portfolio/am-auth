# 📦 Postman Collection - Complete Guide

> **Consolidated from:** POSTMAN_COMPLETE_GUIDE.md + POSTMAN_UPDATE_SUMMARY.md + POSTMAN_COMPARISON.md + POSTMAN_MISSING_ENDPOINTS.md

## 🎯 Overview

Complete Postman collection with **50+ endpoints** covering all services in the AM Authentication System.

### 📊 Coverage Stats

| Metric | Count |
|--------|-------|
| **Total Endpoints** | 50+ |
| **Services Covered** | 5 (API Gateway, User Management, Auth Tokens, Python Service, Java Service) |
| **Folders** | 11 organized categories |
| **Test Scenarios** | Complete authentication flow + all endpoints |

---

## 📁 Collection Structure

```
AM Authentication System
├── 🔐 Authentication Flow (6 endpoints)
│   ├── Register User
│   ├── Activate User
│   ├── Login (OAuth)
│   ├── Validate Token
│   ├── Get Current User Info
│   └── Generate Service Token
│
├── 👤 User Management (10 endpoints)
│   ├── List All Users
│   ├── Get User by ID
│   ├── Update User
│   ├── Delete User
│   ├── Change User Status
│   └── ...more
│
├── 🌐 API Gateway - Documents (3 endpoints)
│   ├── Get My Documents
│   ├── Get All Documents (Admin)
│   └── Documents Service Info
│
├── 🌐 API Gateway - Reports (4 endpoints)
│   ├── Get My Reports
│   ├── Get All Reports
│   ├── Generate Report
│   └── Reports Service Info
│
├── 🌐 API Gateway - Portfolio (2 endpoints)
│   ├── Get My Portfolio
│   └── Record Transaction
│
├── 🌐 API Gateway - Trades (3 endpoints)
│   ├── Get My Trades
│   ├── Execute Trade
│   └── Trades Service Info
│
├── 🌐 API Gateway - Market Data (3 endpoints)
│   ├── Get Market Data
│   ├── Get Stock Quote
│   └── Market Data Service Info
│
├── 🐍 Python Internal Service (5 endpoints)
│   ├── Get Documents
│   ├── Get All Documents
│   ├── Get Document by ID
│   ├── Process Document
│   └── Service Info
│
├── ☕ Java Internal Service (4 endpoints)
│   ├── Get Reports
│   ├── Get All Reports
│   ├── Generate Report
│   └── Service Info
│
├── 🏥 Health Checks (5 endpoints)
│   ├── API Gateway Health
│   ├── User Management Health
│   ├── Auth Tokens Health
│   ├── Python Service Health
│   └── Java Service Health
│
└── 🧪 Testing & Utilities (5+ endpoints)
    ├── Rate Limit Test
    ├── Token Expiry Test
    └── ...more
```

---

## 🚀 Quick Start

### 1. Import Collection

```bash
# File location:
AM_Authentication_System.postman_collection.json

# Import in Postman:
File → Import → Select file → Import
```

### 2. Set Up Environment

Create a new environment with these variables:

| Variable | Initial Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8000` | API Gateway URL |
| `user_url` | `http://localhost:8010` | User Management URL |
| `auth_url` | `http://localhost:8001` | Auth Tokens URL |
| `python_url` | `http://localhost:8002` | Python Service URL (internal) |
| `java_url` | `http://localhost:8003` | Java Service URL (internal) |
| `access_token` | *(auto-set)* | JWT token |
| `service_token` | *(auto-set)* | Service token |
| `user_id` | *(auto-set)* | Current user ID |

### 3. Run Authentication Flow

**Execute in order:**

1. **Register User** → Saves `user_id`
2. **Activate User** → Activates account
3. **Login** → Saves `access_token`
4. **Get Current User** → Verifies token
5. Now you can call any authenticated endpoint!

---

## 🧪 Testing Scenarios

### Scenario 1: Complete User Journey

```
1. Register User
   POST {{user_url}}/api/v1/users/register
   → Get user_id

2. Activate User
   POST {{user_url}}/api/v1/users/{{user_id}}/activate
   → User is now active

3. Login
   POST {{auth_url}}/api/v1/auth/login
   → Get access_token

4. Get My Documents (via API Gateway)
   GET {{base_url}}/api/v1/documents
   → Returns user's documents

5. Get My Reports
   GET {{base_url}}/api/v1/reports
   → Returns user's reports
```

### Scenario 2: Admin Operations

```
1. Login as Admin
   → Get admin access_token

2. Get All Users
   GET {{user_url}}/api/v1/users
   → Returns all users (admin only)

3. Get All Documents
   GET {{base_url}}/api/v1/documents/all
   → Returns all documents (admin only)
```

### Scenario 3: Service-to-Service Auth

```
1. Get Service Token
   POST {{auth_url}}/api/v1/internal/service-token
   → Get service_token

2. Call Python Service
   GET {{python_url}}/internal/service-info
   Header: Authorization: Bearer {{service_token}}
   → Returns service info
```

---

## 🎯 API Gateway vs Direct Access

### ✅ Via API Gateway (Recommended)

```bash
# Access internal services through gateway
GET http://localhost:8000/api/v1/documents
Authorization: Bearer USER_TOKEN

Flow:
1. API Gateway validates user token
2. Generates service token
3. Calls Python service with service token
4. Returns results
```

### ⚠️ Direct Access (Internal Only)

```bash
# Only works from inside Docker network
GET http://am-python-internal-service:8002/internal/documents
Authorization: Bearer SERVICE_TOKEN

Note: Postman CANNOT access this (network isolated)
```

---

## 🔧 Environment Variables Auto-Set

The collection uses **Test Scripts** to automatically set variables:

### After Register User:
```javascript
pm.environment.set("user_id", pm.response.json().user_id);
```

### After Login:
```javascript
pm.environment.set("access_token", pm.response.json().access_token);
```

### After Generate Service Token:
```javascript
pm.environment.set("service_token", pm.response.json().access_token);
```

---

## 📊 Before vs After Comparison

| Feature | Old Collection | New Collection |
|---------|----------------|----------------|
| Total Endpoints | 16 | 50+ |
| API Gateway | ❌ Missing | ✅ Complete |
| Service Coverage | 2 services | 5 services |
| Test Scenarios | Basic | Comprehensive |
| Auto Variables | Manual | Automatic |
| Documentation | Minimal | Detailed |

---

## 🐛 Troubleshooting

### Issue: 401 Unauthorized

**Causes:**
1. Token expired (re-login)
2. User not activated
3. Wrong token format

**Fix:**
```bash
# Re-run authentication flow:
1. Register User (if new)
2. Activate User
3. Login
4. Try request again
```

### Issue: 404 Not Found

**Causes:**
1. Wrong URL
2. Service not running
3. Endpoint doesn't exist

**Fix:**
```bash
# Check services are running:
docker-compose ps

# Check endpoint in Swagger:
http://localhost:8000/docs
```

### Issue: Connection Refused (8002, 8003)

**Cause:** Internal services are network-isolated (this is correct!)

**Fix:** Use API Gateway instead:
```bash
# ❌ DON'T: http://localhost:8002/...
# ✅ DO: http://localhost:8000/api/v1/documents
```

### Issue: 429 Too Many Requests

**Cause:** Rate limit exceeded (100 req/60s)

**Fix:** Wait 60 seconds or increase limit in docker-compose.yml

---

## 🎓 Best Practices

### 1. Use Environments
- Dev: `http://localhost:8000`
- Staging: `https://staging.example.com`
- Prod: `https://api.example.com`

### 2. Organize Folders
- Keep folders collapsed
- Expand only what you're testing
- Use search to find endpoints

### 3. Check Tests Tab
- View auto-set variables
- See validation results
- Debug failures

### 4. Monitor Rate Limits
- Check response headers
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

---

## 📚 Related Files

- `AM_Authentication_System.postman_collection.json` - Main collection
- `postman/README.md` - Postman setup guide
- `postman/QUICK_START.md` - Quick testing guide
- `.github/copilot-instructions.md` - Development patterns

---

## 🎉 What's New

### Additions (34+ new endpoints)
- ✅ API Gateway complete coverage
- ✅ Python internal service endpoints
- ✅ Java internal service endpoints
- ✅ Portfolio, Trades, Market Data
- ✅ Admin operations
- ✅ Health checks

### Improvements
- ✅ Auto-set environment variables
- ✅ Complete test scenarios
- ✅ Better folder organization
- ✅ Detailed descriptions
- ✅ Examples for all endpoints

---

**🚀 Ready to test! Import the collection and start with the Authentication Flow folder.**
