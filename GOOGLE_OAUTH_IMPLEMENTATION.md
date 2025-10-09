# Google OAuth 2.0 Authentication Implementation Guide

## Project Overview
**Service**: am-auth-tokens enhancement  
**Date**: October 9, 2025  
**Objective**: Implement production-ready Google OAuth 2.0 authentication with comprehensive testing

## Updated System Analysis & Requirements
- ✅ FastAPI-based JWT token service with username/password auth
- ✅ PostgreSQL database integration via am-user-management service
- ✅ Docker containerization with service orchestration
- ❌ Missing Google OAuth 2.0 token validation
- ❌ No external provider token verification
- ❌ Limited social authentication options
- 🎯 **PRIMARY GOAL**: Add Google token validation endpoint that extracts email and creates/authenticates users

---

## Refined Implementation Requirements

### 1. Core Google Authentication Features

#### A. Primary Google Token Validation Endpoint
```
POST /api/v1/auth/google/token
```
**Purpose**: Accept Google ID token from client applications and validate it
**Flow**:
1. Receive Google ID token from frontend/mobile app
2. Validate token with Google's public keys
3. Extract user profile (email, name, picture, google_id)
4. Check if user exists in am-user-management service
5. Create new user if doesn't exist, or link to existing user
6. Generate and return internal JWT token

#### B. Supporting Endpoints
```
GET  /api/v1/auth/google/jwks        # Google public keys cache
POST /api/v1/auth/google/refresh     # Refresh internal JWT using Google token
GET  /api/v1/auth/google/profile     # Get user profile from Google token
POST /api/v1/auth/google/link        # Link Google account to existing user
```

### 2. Enhanced Database Schema (via am-user-management)

#### A. User Model Extensions
```sql
-- Extend existing user table
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) DEFAULT 'local';
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS provider_data JSONB;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_google_login TIMESTAMP;

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users(auth_provider);
CREATE INDEX IF NOT EXISTS idx_users_email_verified ON users(email_verified);
```

#### B. OAuth Tokens Table (for refresh tokens)
```sql
CREATE TABLE IF NOT EXISTS oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Production-Ready Security & Features

#### A. Google Token Security
- Verify token signature using Google's public keys (cached locally)
- Validate token audience (aud) matches your Google Client ID
- Check token expiration (exp) and issued time (iat)
- Verify issuer (iss) is accounts.google.com or https://accounts.google.com
- Extract and validate email domain if restrictions needed

#### B. Rate Limiting & Protection
```python
# Rate limiting configuration
GOOGLE_AUTH_RATE_LIMIT = {
    "per_ip": "50/hour",      # 50 requests per hour per IP
    "per_user": "20/hour",    # 20 requests per hour per user
    "global": "1000/hour"     # 1000 total requests per hour
}
```

#### C. Environment Configuration
```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_JWKS_URL=https://www.googleapis.com/oauth2/v3/certs
GOOGLE_ISSUER=https://accounts.google.com
GOOGLE_AUTH_ENABLED=true

# Token Configuration
JWT_GOOGLE_AUDIENCE=your-app-domain.com
JWT_GOOGLE_ISSUER=your-auth-service
JWT_GOOGLE_EXPIRY_HOURS=24
JWT_GOOGLE_REFRESH_DAYS=30

# Security Settings
GOOGLE_TOKEN_CACHE_TTL=3600  # Cache Google public keys for 1 hour
GOOGLE_EMAIL_DOMAINS_ALLOWED=gmail.com,company.com  # Optional domain restriction
```

---

## Comprehensive Testing Strategy (No UI Required)

### 1. Mock Testing Infrastructure

#### A. Google Token Mock Service
```
POST /test/mock/google/token
Body: {
  "email": "testuser@gmail.com",
  "name": "Test User",
  "picture": "https://lh3.googleusercontent.com/test",
  "exp": 3600  // Optional: token expiry in seconds
}
Response: {
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2...",  // Mock Google ID token
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

#### B. Test Environment Setup
```
POST /test/setup/google-auth
Response: {
  "status": "ready",
  "test_client_id": "test-google-client-id",
  "mock_users_created": 5,
  "test_scenarios": [
    "new_user_registration",
    "existing_user_login", 
    "invalid_token_handling",
    "rate_limit_testing"
  ]
}
```

#### C. Test Data Cleanup
```
DELETE /test/cleanup/google-auth
Response: {
  "cleaned": {
    "test_users": 5,
    "oauth_tokens": 3,
    "cached_keys": 1
  }
}
```

### 2. cURL Test Commands

#### Test Complete Google Auth Flow
```bash
#!/bin/bash
echo "=== Google OAuth 2.0 Test Suite ==="

# 1. Setup test environment
echo "1. Setting up test environment..."
curl -X POST http://localhost:8000/test/setup/google-auth

# 2. Generate mock Google token for new user
echo "2. Testing new user registration..."
MOCK_TOKEN=$(curl -s -X POST http://localhost:8000/test/mock/google/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@gmail.com",
    "name": "New Test User",
    "picture": "https://lh3.googleusercontent.com/newuser"
  }' | jq -r '.id_token')

# 3. Authenticate with mock token (should create new user)
echo "3. Authenticating new user with Google token..."
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/google/token \
  -H "Content-Type: application/json" \
  -d "{\"id_token\": \"$MOCK_TOKEN\"}")

echo "Auth Response: $AUTH_RESPONSE"
JWT_TOKEN=$(echo $AUTH_RESPONSE | jq -r '.access_token')

# 4. Verify JWT token works with existing endpoints
echo "4. Testing JWT token with existing endpoints..."
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Authorization: Bearer $JWT_TOKEN"

# 5. Test existing user login
echo "5. Testing existing user login..."
EXISTING_TOKEN=$(curl -s -X POST http://localhost:8000/test/mock/google/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@gmail.com",
    "name": "New Test User"
  }' | jq -r '.id_token')

curl -X POST http://localhost:8000/api/v1/auth/google/token \
  -H "Content-Type: application/json" \
  -d "{\"id_token\": \"$EXISTING_TOKEN\"}"

echo "=== Test Suite Complete ==="
```

#### Rate Limiting Test
```bash
#!/bin/bash
echo "Testing Google Auth Rate Limiting..."

# Generate tokens and test rate limiting
for i in {1..55}; do
  echo "Request $i:"
  curl -s -X POST http://localhost:8000/api/v1/auth/google/token \
    -H "Content-Type: application/json" \
    -d '{"id_token": "invalid-token-for-rate-test"}' \
    -w "Status: %{http_code}, Time: %{time_total}s\n"
  
  # Add small delay every 10 requests
  if (( i % 10 == 0 )); then
    sleep 1
  fi
done
```

#### Security Validation Test
```bash
#!/bin/bash
echo "Testing Google Token Security Validations..."

# Test 1: Invalid token format
echo "1. Invalid token format:"
curl -X POST http://localhost:8000/api/v1/auth/google/token \
  -H "Content-Type: application/json" \
  -d '{"id_token": "invalid.token.format"}'

# Test 2: Expired token (mock)
echo "2. Expired token:"
EXPIRED_TOKEN=$(curl -s -X POST http://localhost:8000/test/mock/google/token \
  -d '{"email": "test@gmail.com", "exp": -3600}' | jq -r '.id_token')
curl -X POST http://localhost:8000/api/v1/auth/google/token \
  -d "{\"id_token\": \"$EXPIRED_TOKEN\"}"

# Test 3: Invalid audience
echo "3. Invalid audience token:"
INVALID_AUD_TOKEN=$(curl -s -X POST http://localhost:8000/test/mock/google/token \
  -d '{"email": "test@gmail.com", "aud": "wrong-client-id"}' | jq -r '.id_token')
curl -X POST http://localhost:8000/api/v1/auth/google/token \
  -d "{\"id_token\": \"$INVALID_AUD_TOKEN\"}"
```

### 3. Automated Test Suite Structure

#### A. Unit Tests
```python
# tests/test_google_auth.py
import pytest
from unittest.mock import patch, MagicMock

class TestGoogleAuthService:
    
    def test_validate_google_token_success(self):
        """Test successful Google token validation"""
        pass
    
    def test_validate_google_token_invalid_signature(self):
        """Test handling of invalid token signature"""
        pass
    
    def test_validate_google_token_expired(self):
        """Test handling of expired tokens"""
        pass
    
    def test_extract_user_profile_from_token(self):
        """Test extraction of user profile data"""
        pass
    
    def test_create_new_user_from_google_profile(self):
        """Test new user creation from Google profile"""
        pass
    
    def test_link_google_account_to_existing_user(self):
        """Test linking Google account to existing user"""
        pass
    
    def test_rate_limiting_enforcement(self):
        """Test rate limiting on Google auth endpoints"""
        pass
    
    def test_jwt_token_generation_after_google_auth(self):
        """Test internal JWT generation after Google auth"""
        pass
```

#### B. Integration Tests
```python
# tests/integration/test_google_auth_flow.py
import pytest
import httpx
from fastapi.testclient import TestClient

class TestGoogleAuthIntegration:
    
    @pytest.mark.asyncio
    async def test_complete_google_auth_flow_new_user(self):
        """Test complete flow for new Google user"""
        pass
    
    @pytest.mark.asyncio  
    async def test_complete_google_auth_flow_existing_user(self):
        """Test complete flow for existing user with Google"""
        pass
    
    @pytest.mark.asyncio
    async def test_google_auth_with_user_management_service(self):
        """Test integration with am-user-management service"""
        pass
```

### 4. Performance & Load Testing

#### A. Performance Test Script
```bash
#!/bin/bash
# load_test_google_auth.sh

echo "Starting Google Auth Performance Test..."

# Test configuration
CONCURRENT_USERS=50
TEST_DURATION=60
BASE_URL="http://localhost:8000"

# Generate test tokens
echo "Generating test tokens..."
for i in $(seq 1 $CONCURRENT_USERS); do
  curl -s -X POST $BASE_URL/test/mock/google/token \
    -d "{\"email\": \"loadtest$i@gmail.com\", \"name\": \"Load Test $i\"}" \
    | jq -r '.id_token' > /tmp/token_$i.txt &
done
wait

echo "Starting load test with $CONCURRENT_USERS concurrent users for ${TEST_DURATION}s..."

# Run concurrent authentication tests
for i in $(seq 1 $CONCURRENT_USERS); do
  {
    TOKEN=$(cat /tmp/token_$i.txt)
    for j in $(seq 1 10); do
      curl -s -X POST $BASE_URL/api/v1/auth/google/token \
        -H "Content-Type: application/json" \
        -d "{\"id_token\": \"$TOKEN\"}" \
        -w "User$i-Request$j: %{http_code} %{time_total}s\n" \
        -o /dev/null
      sleep $((RANDOM % 3 + 1))  # Random delay 1-3 seconds
    done
  } &
done

wait
echo "Load test completed."

# Cleanup
rm -f /tmp/token_*.txt
```

---

## API Endpoints Implementation Plan

### Core Authentication Endpoints
| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/api/v1/auth/google/token` | **Primary**: Validate Google ID token & return JWT | 🔴 Critical |
| GET | `/api/v1/auth/google/jwks` | Cache Google public keys | 🟡 High |
| POST | `/api/v1/auth/google/refresh` | Refresh internal JWT | 🟡 High |
| GET | `/api/v1/auth/google/profile` | Get profile from Google token | 🟢 Medium |
| POST | `/api/v1/auth/google/link` | Link Google to existing account | 🟢 Medium |

### Testing & Development Endpoints
| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| POST | `/test/mock/google/token` | Generate mock Google tokens | 🔴 Critical |
| POST | `/test/setup/google-auth` | Setup test environment | 🔴 Critical |
| DELETE | `/test/cleanup/google-auth` | Clean test data | 🟡 High |
| GET | `/test/scenarios/google-auth` | List available test scenarios | 🟢 Medium |

### Health & Monitoring
| Method | Endpoint | Description | Priority |
|--------|----------|-------------|----------|
| GET | `/health/google` | Google API connectivity | 🟡 High |
| GET | `/metrics/google-auth` | Authentication metrics | 🟢 Medium |

---

## Expected Response Formats

### Successful Google Authentication
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@gmail.com",
    "name": "User Name", 
    "picture": "https://lh3.googleusercontent.com/...",
    "email_verified": true,
    "auth_provider": "google",
    "is_new_user": false,
    "google_id": "117234567890123456789"
  },
  "scopes": ["read", "write"]
}
```

### Error Responses
```json
// Invalid Token
{
  "success": false,
  "error": "invalid_token",
  "error_description": "The Google ID token is invalid or malformed",
  "error_code": "GOOGLE_TOKEN_INVALID",
  "status_code": 401
}

// Rate Limited
{
  "success": false,
  "error": "rate_limit_exceeded", 
  "error_description": "Too many authentication requests. Try again later.",
  "retry_after": 3600,
  "status_code": 429
}

// Service Error
{
  "success": false,
  "error": "service_unavailable",
  "error_description": "Unable to validate token with Google services",
  "error_code": "GOOGLE_SERVICE_DOWN",
  "status_code": 503
}
```

---

## Implementation Phases & Timeline

### Phase 1: Foundation (Days 1-3)
- [ ] Setup Google token validation infrastructure
- [ ] Create mock Google token generator for testing
- [ ] Implement basic `/api/v1/auth/google/token` endpoint
- [ ] Add database schema changes to am-user-management
- [ ] Create initial test suite with cURL commands

### Phase 2: Core Features (Days 4-6)
- [ ] Complete Google token signature verification
- [ ] User creation/linking logic with am-user-management service
- [ ] JWT token generation after Google auth
- [ ] Comprehensive error handling
- [ ] Rate limiting implementation

### Phase 3: Security & Testing (Days 7-9)
- [ ] Security validations (audience, issuer, expiry)
- [ ] Performance testing and optimization
- [ ] Load testing with concurrent users
- [ ] Security penetration testing
- [ ] Monitoring and metrics collection

### Phase 4: Production Ready (Days 10-12)
- [ ] Docker configuration updates
- [ ] Environment variable management
- [ ] Health checks and monitoring
- [ ] Documentation completion
- [ ] Deployment procedures

---

## Success Criteria & Validation

### Functional Requirements ✅
- [ ] Google ID tokens are successfully validated
- [ ] User profiles are extracted and stored correctly
- [ ] New users are created automatically
- [ ] Existing users can link Google accounts
- [ ] Internal JWT tokens are generated and valid
- [ ] Integration with am-user-management service works

### Performance Requirements ⚡
- [ ] Handle 50 concurrent authentication requests
- [ ] Response time < 500ms for token validation
- [ ] Rate limiting prevents abuse (50 req/hour per IP)
- [ ] System remains stable under load

### Security Requirements 🔒
- [ ] Token signature verification works correctly
- [ ] Expired tokens are rejected
- [ ] Invalid audience/issuer tokens are rejected
- [ ] Rate limiting prevents brute force attacks
- [ ] No sensitive data in error messages

### Testing Requirements 🧪
- [ ] 90% test coverage for Google auth features
- [ ] All test scenarios pass without UI
- [ ] Load testing validates performance requirements
- [ ] Security testing validates protection mechanisms

---

## Quick Start Commands

```bash
# 1. Start services
docker-compose up -d

# 2. Verify services are running
curl http://localhost:8000/health
curl http://localhost:8001/health

# 3. Setup Google auth testing
curl -X POST http://localhost:8000/test/setup/google-auth

# 4. Run complete test suite
./test_google_auth_complete.sh

# 5. Load test (optional)
./load_test_google_auth.sh

# 6. View logs
docker-compose logs -f auth-tokens
```

This implementation guide provides a comprehensive roadmap for adding production-ready Google OAuth 2.0 authentication to your auth-tokens service with extensive testing capabilities that don't require any UI components.