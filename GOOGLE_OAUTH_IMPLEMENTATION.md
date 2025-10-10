# Google OAuth 2.0 Implementation Prompt

## IMPLEMENTATION PROMPT FOR DEVELOPER

**Task**: Implement Google OAuth 2.0 token validation in am-auth-tokens service

**Current System**: FastAPI JWT service with PostgreSQL, Docker setup, am-user-management integration

## DEVELOPER PROMPT: IMPLEMENT GOOGLE OAUTH 2.0

**IMMEDIATE TASK**: Build Google token validation endpoint in am-auth-tokens service that:

1. **Accepts Google ID tokens from clients**
2. **Validates tokens with Google's public keys**  
3. **Extracts user email and profile information**
4. **Creates/links users in am-user-management service**
5. **Returns internal JWT tokens for session management**

---

## STEP-BY-STEP IMPLEMENTATION REQUIREMENTS

### STEP 1: CREATE PRIMARY ENDPOINT
**Build**: `POST /api/v1/auth/google/token` endpoint that:

```python
# Request Format
{
  "id_token": "eyJhbGciOiJSUzI1NiIs..."  # Google ID token from client
}

# Response Format  
{
  "access_token": "your_jwt_token_here",
  "token_type": "bearer", 
  "expires_in": 86400,
  "user": {
    "email": "user@gmail.com",
    "name": "User Name",
    "picture": "profile_url",
    "is_new_user": true
  }
}
```

**Implementation Steps**:
1. Install dependencies: `google-auth`, `cryptography`, `requests`
2. Create Google token validator service class
3. Verify token signature against Google's JWKS
4. Extract claims (email, name, picture, sub)
5. Call am-user-management to create/fetch user
6. Generate internal JWT token
7. Return standardized response

### STEP 2: CREATE TESTING INFRASTRUCTURE
**Build**: Mock testing endpoints for development without UI:

```python
# Testing Endpoints to Create
POST /test/mock/google/token     # Generate fake Google tokens for testing
POST /test/setup                 # Setup test environment  
DELETE /test/cleanup             # Clean test data
```

**Mock Token Generator**: Create endpoint that generates valid JWT tokens with Google-like claims for testing without real Google integration.

### STEP 3: UPDATE DATABASE SCHEMA
**Modify**: am-user-management service to support Google users:

```sql
-- Add these columns to existing users table
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN auth_provider VARCHAR(50) DEFAULT 'local';  
ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500);
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;

-- Add performance indexes
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_provider ON users(auth_provider);
```

**Update am-user-management endpoints**:
- Modify user creation to handle Google profiles
- Add endpoint to find user by google_id
- Update user model/schema classes

### STEP 4: ADD SECURITY & CONFIGURATION
**Security Requirements**:
```python
# Google Token Validation Checklist
✓ Verify JWT signature with Google public keys
✓ Check token expiration (exp claim)
✓ Validate audience (aud) matches your client ID  
✓ Verify issuer is Google (accounts.google.com)
✓ Rate limit: 50 requests/hour per IP

# Environment Variables to Add
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret  
GOOGLE_AUTH_ENABLED=true
JWT_EXPIRY_HOURS=24
```

**Rate Limiting**: Add middleware to prevent abuse (slowapi or similar)
**Error Handling**: Return consistent error formats
**Logging**: Log all authentication attempts

### STEP 5: IMPLEMENT TESTING (No UI Required)
**Create these test commands**:

**A. Quick Test Commands**:
```bash
# 1. Generate mock Google token
curl -X POST http://localhost:8000/test/mock/google/token \
  -d '{"email": "test@gmail.com", "name": "Test User"}'

# 2. Test Google authentication  
curl -X POST http://localhost:8000/api/v1/auth/google/token \
  -d '{"id_token": "MOCK_TOKEN_FROM_STEP_1"}'

# 3. Verify JWT works with existing endpoints
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Authorization: Bearer JWT_FROM_STEP_2"
```

**B. Test Scenarios to Validate**:
- ✅ New user registration via Google token
- ✅ Existing user login via Google token  
- ✅ Invalid/expired token rejection
- ✅ Rate limiting works (try 60+ requests)
- ✅ JWT tokens work with existing endpoints

---

## IMPLEMENTATION CHECKLIST

### Dependencies to Install:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 cryptography
```

### Files to Create/Modify:
- [ ] `app/services/google_auth.py` - Google token validation service
- [ ] `app/api/v1/endpoints/google_auth.py` - Google auth endpoints  
- [ ] `app/api/v1/endpoints/test_endpoints.py` - Mock testing endpoints
- [ ] Update `requirements.txt` with new dependencies
- [ ] Update `docker-compose.yml` with Google env vars
- [ ] Add database migration for user schema changes

### Core Implementation Functions:
```python
class GoogleAuthService:
    def validate_id_token(self, id_token: str) -> dict
    def extract_user_profile(self, token_data: dict) -> dict  
    def create_or_get_user(self, profile: dict) -> dict
    def generate_internal_jwt(self, user: dict) -> str
```

### Testing Strategy:
- [ ] Build mock token generator (`POST /test/mock/google/token`)
- [ ] Test with cURL commands (no UI needed)
- [ ] Validate rate limiting (50+ requests)  
- [ ] Test error handling (invalid tokens)
- [ ] Verify integration with existing JWT validation

### Expected Response Format:
```json
{
  "access_token": "your_jwt_here",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "email": "user@gmail.com",
    "name": "User Name",
    "is_new_user": true
  }
}
```

---

## IMPLEMENTATION TIMELINE

**Week 1**: Core Google token validation endpoint + mock testing
**Week 2**: Database integration + security features + production testing

## SUCCESS CRITERIA
✅ Accept Google ID tokens from clients  
✅ Validate tokens with Google's servers  
✅ Extract user email and profile data  
✅ Create/link users automatically  
✅ Return internal JWT tokens  
✅ Test without UI using cURL commands  
✅ Handle 50+ concurrent requests  
✅ Production-ready security (rate limiting, validation)

**START HERE**: Begin with Step 1 - create the primary endpoint and mock testing infrastructure.