# 🚀 Complete Postman Collection - User Guide

## 📊 What's New?

Your **NEW** collection has **50+ endpoints** (up from 16):

### ✅ Added Collections:
1. **🌐 API Gateway** (15 endpoints) - Documents, Reports, Portfolio, Trading, Market Data
2. **🔑 Token Management** (7 endpoints) - Complete token operations
3. **👥 User Management** (6 endpoints) - User status and management
4. **🏢 Service Management** (4 endpoints) - Register and manage services
5. **Enhanced Security Tests** - More comprehensive testing

---

## 🎯 How to Use

### Step 1: Import the Collection

```bash
# Open Postman
# File → Import
# Select: AM_Authentication_System_COMPLETE.postman_collection.json
```

### Step 2: Create Environment (Optional but Recommended)

Create a new environment with these variables:
- `user_access_token` - Auto-saved during login
- `service_token` - Auto-saved when generated
- `user_id` - Auto-saved during registration
- `test_email` - testuser@example.com

### Step 3: Run Authentication Flow (REQUIRED FIRST)

**Execute in order:**

1. **Register User** → Creates new user account
2. **Activate User** → ⚠️ **REQUIRED** - Must activate before login
3. **Login** → Gets JWT token (auto-saved to `{{user_access_token}}`)
4. **Validate Token** → Verify token works
5. **Get Current User Info** → Get user details from token
6. **Generate Service Token** → Get service token (auto-saved to `{{service_token}}`)

✅ Now you can test any other endpoint!

---

## 📂 Collection Structure

### 🔐 Authentication Flow (Start Here)
- Complete registration → activation → login flow
- Tokens auto-saved for reuse

### 🌐 API Gateway Folders

#### Documents
- `GET /api/v1/documents` - Your documents (user token)
- `GET /api/v1/documents/all` - All documents (service token)
- `GET /api/v1/documents/service-info` - Service info

#### Reports
- `GET /api/v1/reports` - Your reports (user token)
- `GET /api/v1/reports/all` - All reports (service token)
- `POST /api/v1/reports/generate` - Generate report (user token)
- `GET /api/v1/reports/service-info` - Service info

#### Portfolio (NEW!)
- `GET /api/v1/portfolio` - Your portfolio
- `POST /api/v1/portfolio/transaction` - Record transaction

#### Trading (NEW!)
- `GET /api/v1/trades` - Your trades
- `POST /api/v1/trades/execute` - Execute trade

#### Market Data (NEW!)
- `GET /api/v1/market-data/stocks/{symbol}` - Get stock quote
- `GET /api/v1/market-data/quotes` - Get market quotes

### 🔑 Token Management
- Generate tokens (basic, by user ID, service)
- Validate tokens (multiple methods)
- Introspect tokens
- Get service permissions
- List all services

### 👥 User Management
- Get/Update user status (by ID or email)
- Get user by Google ID
- Get auth status
- Reset database (admin)

### 🏢 Service Management
- Register service
- Update service
- Get service status
- Validate service credentials

### 🔐 Google OAuth Flow
- Mock Google token generation
- Google authentication
- Google OAuth info

### 🔍 Health Checks
- All services (API Gateway, User Management, Auth Tokens)
- Service info endpoints

### 🧪 Security Tests
- No token tests (should fail 403)
- Invalid token tests (should fail 401)
- Wrong credentials tests (should fail 401)
- Network isolation tests (should fail - connection refused)

---

## 🎯 Quick Test Scenarios

### Scenario 1: Test Documents API (5 min)

1. Run **Authentication Flow** folder (all 6 requests)
2. Open **API Gateway - Documents** folder
3. Run **Get My Documents** → See your documents
4. Run **Get All Documents** → See all (requires service token)

### Scenario 2: Test Reports Generation (5 min)

1. Ensure authenticated (run Authentication Flow)
2. Open **API Gateway - Reports** folder
3. Run **Generate Report** → Creates new report
4. Run **Get My Reports** → See your reports

### Scenario 3: Test Portfolio Management (5 min)

1. Ensure authenticated
2. Open **API Gateway - Portfolio** folder
3. Run **Record Transaction** → Add AAPL purchase
4. Run **Get My Portfolio** → See your portfolio

### Scenario 4: Test Trading (5 min)

1. Ensure authenticated
2. Open **API Gateway - Trading** folder
3. Run **Execute Trade** → Buy TSLA shares
4. Run **Get My Trades** → See trade history

### Scenario 5: Test Market Data (2 min)

1. Ensure authenticated
2. Open **API Gateway - Market Data** folder
3. Run **Get Stock Quote** → Get AAPL quote
4. Run **Get Market Quotes** → Get multiple quotes

### Scenario 6: Security Testing (5 min)

1. Open **Security Tests** folder
2. Run **No Token** → Should fail with 403
3. Run **Invalid Token** → Should fail with 401
4. Run **Internal Service** → Should fail (connection refused)

### Scenario 7: Service Management (10 min)

1. Ensure authenticated
2. Open **Service Management** folder
3. Run **Register Service** → Create new service
4. Run **Get Service Status** → Check status
5. Run **Validate Service Credentials** → Test credentials

---

## 🔑 Token Types

### User Access Token (`{{user_access_token}}`)
- **Purpose**: Authenticate as a user
- **Use for**: 
  - Get MY documents/reports/portfolio/trades
  - Generate reports
  - Execute trades
  - Record transactions
- **Get from**: Login request (step 3)

### Service Token (`{{service_token}}`)
- **Purpose**: Authenticate as internal service
- **Use for**:
  - Get ALL documents/reports
  - Access service-info endpoints
  - Internal service operations
- **Get from**: Generate Service Token (step 6)

---

## 🎨 Expected Responses

### ✅ Success Scenarios

```json
// User Documents (200 OK)
{
  "status": "success",
  "data": {
    "documents": [...],
    "user_id": "123"
  }
}

// Generate Report (200 OK)
{
  "report_id": "abc-123",
  "status": "generated",
  "report_name": "My Test Report"
}

// Execute Trade (200 OK)
{
  "trade_id": "trade-456",
  "symbol": "TSLA",
  "status": "executed"
}
```

### ❌ Error Scenarios

```json
// No Token (403 Forbidden)
{
  "detail": "Not authenticated"
}

// Invalid Token (401 Unauthorized)
{
  "detail": "Could not validate credentials"
}

// Internal Service (Connection Refused)
Error: connect ECONNREFUSED 127.0.0.1:8002
// ✅ This is CORRECT - network isolation working!
```

---

## 🐛 Troubleshooting

### Issue: "Not authenticated" (403)
**Solution**: 
1. Run Authentication Flow first
2. Check `{{user_access_token}}` is set
3. Re-login if token expired (60 min default)

### Issue: "Could not validate credentials" (401)
**Solution**:
1. Token may be expired - re-login
2. Check token is correctly saved in environment
3. Verify token format: `Bearer <token>`

### Issue: Connection refused on 8002 or 8003
**Solution**: 
- ✅ This is CORRECT behavior!
- Internal services are NOT accessible externally
- This is network isolation security working
- Access through API Gateway (port 8000) instead

### Issue: User not found after registration
**Solution**:
- ⚠️ You MUST activate user (step 2) before login
- Run "Activate User" request
- Then try login again

### Issue: Service token not working
**Solution**:
1. Verify you have user token first
2. Generate service token requires user token
3. Check permissions in request body
4. Service token has different claims than user token

---

## 📊 Comparison: Old vs New Collection

| Category | Old Collection | New Collection |
|----------|---------------|----------------|
| **Total Endpoints** | 16 | 50+ |
| **API Gateway** | ❌ 0 | ✅ 15 |
| **Token Management** | ✅ 4 | ✅ 11 |
| **User Management** | ✅ 3 | ✅ 9 |
| **Service Management** | ❌ 0 | ✅ 4 |
| **Portfolio** | ❌ 0 | ✅ 2 |
| **Trading** | ❌ 0 | ✅ 2 |
| **Market Data** | ❌ 0 | ✅ 2 |
| **Google OAuth** | ✅ 3 | ✅ 3 |
| **Security Tests** | ✅ 3 | ✅ 4 |
| **Health Checks** | ✅ 4 | ✅ 5 |

---

## 🎯 Testing Checklist

Use this checklist to test all functionality:

### Authentication ✅
- [ ] Register user
- [ ] Activate user
- [ ] Login with OAuth
- [ ] Validate token
- [ ] Get current user info
- [ ] Generate service token

### API Gateway - Documents ✅
- [ ] Get my documents
- [ ] Get all documents (service token)
- [ ] Get service info

### API Gateway - Reports ✅
- [ ] Get my reports
- [ ] Get all reports (service token)
- [ ] Generate report
- [ ] Get service info

### API Gateway - Portfolio ✅
- [ ] Get my portfolio
- [ ] Record transaction

### API Gateway - Trading ✅
- [ ] Get my trades
- [ ] Execute trade

### API Gateway - Market Data ✅
- [ ] Get stock quote
- [ ] Get market quotes

### Token Management ✅
- [ ] Generate basic token
- [ ] Generate token by user ID
- [ ] Generate service token (public)
- [ ] Validate bearer token
- [ ] Introspect token
- [ ] Get service permissions
- [ ] List all services

### User Management ✅
- [ ] Get user status by ID
- [ ] Update user status by ID
- [ ] Get user status by email
- [ ] Get user by Google ID
- [ ] Get auth status

### Service Management ✅
- [ ] Register service
- [ ] Update service
- [ ] Get service status
- [ ] Validate credentials

### Security ✅
- [ ] No token fails (403)
- [ ] Invalid token fails (401)
- [ ] Wrong credentials fails (401)
- [ ] Internal service fails (connection refused)

---

## 💡 Pro Tips

1. **Use Postman Environments** - Save tokens across sessions
2. **Run folders in order** - Use "Run Collection" feature
3. **Check Console** - See auto-saved variables
4. **Use Tests tab** - View response assertions
5. **Save responses** - Use "Save Response" for documentation

---

## 📚 Related Documentation

- **README.md** - Project overview
- **docs/TESTING.md** - Complete testing guide
- **docs/QUICK_START.md** - 5-minute setup
- **docs/API_GATEWAY_IMPLEMENTATION.md** - Implementation details
- **POSTMAN_MISSING_ENDPOINTS.md** - What was missing analysis

---

## 🎉 Summary

You now have a **COMPLETE Postman collection** with:

✅ **50+ endpoints** covering all services
✅ **Organized folders** for easy navigation
✅ **Auto-saved tokens** for seamless testing
✅ **Security tests** to verify protection
✅ **Complete API Gateway** coverage
✅ **Service management** capabilities
✅ **User management** operations
✅ **Trading & Portfolio** features
✅ **Market data** access

**Next Steps:**
1. Import `AM_Authentication_System_COMPLETE.postman_collection.json`
2. Run "🔐 Authentication Flow" folder
3. Test any endpoint you want!

Happy Testing! 🚀
