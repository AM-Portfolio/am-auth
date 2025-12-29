# 🔐 Security Architecture - Authentication & Authorization System

## Core Principles

**Zero Trust Architecture with Multi-Tier Authentication:**
- ✅ All services independently validate JWT tokens
- ✅ User authentication via access/refresh token pairs
- ✅ Service-to-service authentication via internal JWT
- ✅ Port isolation for internal services
- ✅ Complete audit trail through API Gateway
- ✅ Frontend integration with secure token management

---

## Network Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              HOST MACHINE                                            │
│                                                                                      │
│  Flutter Frontend / Postman / Client Application                                    │
│         │                                                                            │
│         │ (User JWT - Access/Refresh Tokens)                                        │
│         │                                                                            │
│         ▼                                                                            │
│    ┌─────────────────────────────────────────────────────────────────────────────┐ │
│    │              API Gateway (Port 8000) ✅ EXPOSED                             │ │
│    │  • Validates user JWT (access tokens)                                       │ │
│    │  • Routes to auth services                                                  │ │
│    │  • Generates service JWT for internal calls                                 │ │
│    │  • Proxies requests to all internal services                                │ │
│    └─────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                             │
│                                        │ Docker Network (am-network)                 │
│         ┌──────────────────────────────┼──────────────────────────────┐             │
│         │                              │                              │             │
│         ▼                              ▼                              ▼             │
│  ┌─────────────┐              ┌─────────────┐              ┌─────────────┐         │
│  │   Auth      │              │    User     │              │  Document   │         │
│  │   Tokens    │              │ Management  │              │  Processor  │         │
│  │  (8001) ✅  │              │  (8010) ✅  │              │  (8070) ❌  │         │
│  │  EXPOSED    │              │  EXPOSED    │              │ NOT EXPOSED │         │
│  │             │              │             │              │             │         │
│  │ • Login     │              │ • Register  │              │ • Process   │         │
│  │ • Refresh   │              │ • Profile   │              │   Docs      │         │
│  │ • Logout    │              │ • Activate  │              │ • Validate  │         │
│  │ • Google    │              │             │              │   Service   │         │
│  │             │              │             │              │   JWT       │         │
│  └─────────────┘              └─────────────┘              └─────────────┘         │
│         │                              │                              │             │
│         └──────────────────────────────┼──────────────────────────────┘             │
│                                        │                                             │
│                                        │ Internal Network Only                       │
│         ┌──────────────────────────────┼──────────────────────────────┐             │
│         │                              │                              │             │
│         ▼                              ▼                              ▼             │
│  ┌─────────────┐              ┌─────────────┐              ┌─────────────┐         │
│  │  Portfolio  │              │  Trade API  │              │   Market    │         │
│  │   Service   │              │   Service   │              │    Data     │         │
│  │  (8080) ❌  │              │  (8073) ❌  │              │  (8092) ❌  │         │
│  │ NOT EXPOSED │              │ NOT EXPOSED │              │ NOT EXPOSED │         │
│  │             │              │             │              │             │         │
│  │ • Holdings  │              │ • Orders    │              │ • Prices    │         │
│  │ • Assets    │              │ • Trades    │              │ • Quotes    │         │
│  │ • Analytics │              │ • History   │              │ • History   │         │
│  │ • Reports   │              │ • Positions │              │ • Analytics │         │
│  └─────────────┘              └─────────────┘              └─────────────┘         │
│         │                              │                              │             │
│         └──────────────────────────────┼──────────────────────────────┘             │
│                                        │                                             │
│         ┌──────────────────────────────┴──────────────────────────────┐             │
│         │                                                              │             │
│         ▼                                                              ▼             │
│  ┌─────────────┐                                              ┌─────────────┐       │
│  │   Python    │                                              │    Java     │       │
│  │  Internal   │                                              │  Internal   │       │
│  │  (8002) ❌  │                                              │  (8003) ❌  │       │
│  │ NOT EXPOSED │                                              │ NOT EXPOSED │       │
│  │             │                                              │             │       │
│  │ • Document  │                                              │ • Reports   │       │
│  │   Analysis  │                                              │ • Analytics │       │
│  │ • Data Proc │                                              │ • Business  │       │
│  │             │                                              │   Logic     │       │
│  └─────────────┘                                              └─────────────┘       │
│                                                                                      │
│                     All Internal Services Validate Service JWT                      │
│                     (INTERNAL_JWT_SECRET - Never Exposed to Clients)                │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Service Ports

| Service | Port | Exposed | Access From | Purpose |
|---------|------|---------|-------------|---------|
| **API Gateway** | **8000** | **✅ YES** | **Host/Client** | **Single entry point, routing to all services** |
| **Auth Tokens** | **8001** | **✅ YES** | **Host/Client** | **Login, token management, logout, Google OAuth** |
| **User Management** | **8010** | **✅ YES** | **Host/Client** | **Registration, profile, activation** |
| Document Processor | 8070 | ❌ NO | Internal Network Only | Document processing, validation |
| Portfolio Service | 8080 | ❌ NO | Internal Network Only | Holdings, assets, analytics, reports |
| Trade API | 8073 | ❌ NO | Internal Network Only | Orders, trades, history, positions |
| Market Data | 8092 | ❌ NO | Internal Network Only | Prices, quotes, market history, analytics |
| Python Internal Service | 8002 | ❌ NO | Internal Network Only | Document analysis, data processing |
| Java Internal Service | 8003 | ❌ NO | Internal Network Only | Reports, analytics, business logic |

**Security Note:** Only 3 services are exposed to the host machine (API Gateway, Auth Tokens, User Management). All other services are accessible only through the API Gateway via the internal Docker network, providing defense-in-depth security.

**Note on Redis:** Redis caching is configured but currently disabled (`ENABLE_REDIS_CACHING=false`). The Redis service has been removed from the architecture to reduce unnecessary services.

---

## Authentication System Overview

### Token Types

#### 1. Access Tokens (User Authentication)
- **Purpose:** Short-lived tokens for API access
- **Lifetime:** 30 minutes
- **Issued by:** `am-auth-tokens` service
- **Validated by:** All services independently
- **Storage:** Frontend memory/secure storage
- **Format:** JWT with HS256 signature

**Token Structure:**
```json
{
  "sub": "user@example.com",
  "user_id": "uuid-of-user",
  "email": "user@example.com",
  "scopes": ["read", "write"],
  "exp": 1234567890,
  "iat": 1234567800,
  "type": "access"
}
```

#### 2. Refresh Tokens (Token Renewal)
- **Purpose:** Long-lived tokens for obtaining new access tokens
- **Lifetime:** 7 days
- **Issued by:** `am-auth-tokens` service
- **Validated by:** `am-auth-tokens` service only
- **Storage:** Frontend secure storage (HttpOnly cookies recommended)
- **Rotation:** New refresh token issued on each use
- **Revocation:** Stored in database, can be revoked

**Token Structure:**
```json
{
  "sub": "user@example.com",
  "user_id": "uuid-of-user",
  "token_id": "unique-token-id",
  "exp": 1234567890,
  "iat": 1234567800,
  "type": "refresh"
}
```

#### 3. Service Tokens (Internal Communication)
- **Purpose:** Service-to-service authentication
- **Lifetime:** 15 minutes
- **Issued by:** API Gateway
- **Validated by:** Internal services
- **Storage:** Never exposed to clients
- **Secret:** `INTERNAL_JWT_SECRET` (different from user tokens)

**Token Structure:**
```json
{
  "user_id": "uuid-of-authenticated-user",
  "service_id": "document-processor",
  "type": "service",
  "exp": 1234567890,
  "iat": 1234567800
}
```

---

## Authentication Flows

### Flow 1: User Registration

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ 1. POST /user/api/v1/auth/register
       │    { email, password, phone_number }
       ▼
┌──────────────────────────────────────┐
│   User Management Service (8010)     │
│   ✅ Validates email format          │
│   ✅ Checks password strength         │
│   ✅ Creates user account             │
│   ✅ Sends verification email         │
└──────┬───────────────────────────────┘
       │ 2. Returns user_id
       ▼
┌──────────────────────────────────────┐
│   Frontend                           │
│   ✅ Shows success message           │
│   ✅ Redirects to login              │
└──────────────────────────────────────┘
```

**Registration Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "phone_number": "+1234567890"
}
```

**Registration Response:**
```json
{
  "user_id": "uuid-of-new-user",
  "email": "user@example.com",
  "status": "pending_verification",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Flow 2: User Login (Email/Password)

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ 1. POST /api/v1/tokens
       │    username=email&password=password (form-urlencoded)
       ▼
┌──────────────────────────────────────┐
│   Auth Tokens Service (8001)         │
│   ✅ Validates credentials           │
│   ✅ Generates access token          │
│   ✅ Generates refresh token         │
│   ✅ Stores refresh token in DB      │
└──────┬───────────────────────────────┘
       │ 2. Returns tokens + user info
       ▼
┌──────────────────────────────────────┐
│   Frontend                           │
│   ✅ Stores access token (memory)    │
│   ✅ Stores refresh token (secure)   │
│   ✅ Updates auth state              │
│   ✅ Redirects to dashboard          │
└──────────────────────────────────────┘
```

**Login Request (OAuth2 Password Flow):**
```
POST /api/v1/tokens
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123!
```

**Login Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "user_id": "uuid-of-user",
    "email": "user@example.com",
    "username": "user@example.com",
    "status": "active",
    "scopes": ["read", "write"]
  }
}
```

---

### Flow 3: Google Sign-In

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ 1. Initiates Google Sign-In (client-side)
       │    Uses google_sign_in package
       ▼
┌──────────────────────────────────────┐
│   Google OAuth                       │
│   ✅ User authenticates              │
│   ✅ Returns ID token                │
└──────┬───────────────────────────────┘
       │ 2. ID token
       ▼
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ 3. POST /api/v1/auth/google/token
       │    { id_token }
       ▼
┌──────────────────────────────────────┐
│   Auth Tokens Service (8001)         │
│   ✅ Validates Google ID token       │
│   ✅ Creates/updates user            │
│   ✅ Generates access token          │
│   ✅ Generates refresh token         │
└──────┬───────────────────────────────┘
       │ 4. Returns tokens + user info
       ▼
┌──────────────────────────────────────┐
│   Frontend                           │
│   ✅ Stores tokens                   │
│   ✅ Updates auth state              │
│   ✅ Redirects to dashboard          │
└──────────────────────────────────────┘
```

**Google Login Request:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

---

### Flow 4: Token Refresh

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ 1. Access token expired
       │    POST /api/v1/auth/refresh
       │    { refresh_token }
       ▼
┌──────────────────────────────────────┐
│   Auth Tokens Service (8001)         │
│   ✅ Validates refresh token         │
│   ✅ Checks if revoked               │
│   ✅ Generates new access token      │
│   ✅ Generates new refresh token     │
│   ✅ Revokes old refresh token       │
└──────┬───────────────────────────────┘
       │ 2. Returns new tokens
       ▼
┌──────────────────────────────────────┐
│   Frontend                           │
│   ✅ Updates stored tokens           │
│   ✅ Retries failed request          │
└──────────────────────────────────────┘
```

**Refresh Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Refresh Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

---

### Flow 5: Logout

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ 1. POST /api/v1/auth/logout
       │    Authorization: Bearer {access_token}
       ▼
┌──────────────────────────────────────┐
│   Auth Tokens Service (8001)         │
│   ✅ Validates access token          │
│   ✅ Revokes all refresh tokens      │
│   ✅ Logs logout event               │
└──────┬───────────────────────────────┘
       │ 2. Returns success
       ▼
┌──────────────────────────────────────┐
│   Frontend                           │
│   ✅ Clears stored tokens            │
│   ✅ Clears auth state               │
│   ✅ Redirects to login              │
└──────────────────────────────────────┘
```

---

### Flow 6: Client → API Gateway → Internal Service

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │ 1. API request with user access token
       │    Authorization: Bearer {access_token}
       ▼
┌──────────────────────────────────────┐
│   API Gateway (8000)                 │
│   ✅ Validates user access token     │
│   ✅ Extracts user_id                │
│   ✅ Generates service JWT           │
│   ✅ Proxies to internal service     │
└──────┬───────────────────────────────┘
       │ 2. Service JWT (internal network)
       │    Authorization: Bearer {service_token}
       ▼
┌──────────────────────────────────────┐
│   Document Processor (8070)          │
│   ✅ Validates service JWT           │
│   ✅ Processes request               │
│   ✅ Returns result                  │
└──────┬───────────────────────────────┘
       │ 3. Response
       ▼
┌──────────────────────────────────────┐
│   API Gateway                        │
│   ✅ Proxies response to client      │
└──────┬───────────────────────────────┘
       │ 4. Response
       ▼
┌──────────────┐
│   Frontend   │
└──────────────┘
```

**Security Properties:**
- ✅ Client authenticates as user (not service)
- ✅ Service tokens never exposed to client
- ✅ Service tokens never leave internal network
- ✅ Complete audit trail
- ✅ Defense in depth

---

## Frontend Integration

### Authentication State Management

**Flutter Architecture:**
- **State Management:** `flutter_bloc` with `AuthCubit`
- **Data Layer:** Repository pattern with remote/mock data sources
- **Domain Layer:** Use cases for each auth operation
- **Presentation Layer:** BLoC/Cubit for state management

**Key Components:**
```
lib/features/authentication/
├── data/
│   ├── datasources/
│   │   ├── auth_remote_datasource.dart  # API calls
│   │   └── mock_auth_datasource.dart    # Testing
│   ├── models/
│   │   ├── auth_result_model.dart       # Login/register response
│   │   └── auth_tokens_model.dart       # Token pair
│   └── repositories/
│       └── auth_repository_impl.dart    # Repository implementation
├── domain/
│   ├── entities/
│   │   ├── auth_result_entity.dart
│   │   └── user_entity.dart
│   ├── repositories/
│   │   └── auth_repository.dart         # Abstract repository
│   └── usecases/
│       ├── email_login_usecase.dart
│       ├── google_login_usecase.dart
│       ├── register_usecase.dart
│       └── logout_usecase.dart
└── presentation/
    ├── cubit/
    │   ├── auth_cubit.dart              # State management
    │   └── auth_state.dart              # Auth states
    └── pages/
        ├── login_screen.dart
        ├── register_page.dart
        └── auth_wrapper.dart            # Route guard
```

### API Endpoints (Frontend Constants)

```dart
class AuthConstants {
  // Authentication endpoints
  static const String loginEndpoint = '/api/v1/tokens';
  static const String googleLoginEndpoint = '/api/v1/auth/google/token';
  static const String registerEndpoint = '/user/api/v1/auth/register';
  static const String refreshTokenEndpoint = '/api/v1/auth/refresh';
  static const String logoutEndpoint = '/api/v1/auth/logout';
  
  // Token configuration
  static const int accessTokenExpiry = 1800; // 30 minutes
  static const int refreshTokenExpiry = 604800; // 7 days
}
```

### Token Storage Strategy

**Access Tokens:**
- Stored in memory (AuthCubit state)
- Never persisted to disk
- Cleared on app restart

**Refresh Tokens:**
- Stored in secure storage (`flutter_secure_storage`)
- Encrypted at rest
- Used to restore session on app restart

**Recommended Enhancement:**
- Implement HttpOnly cookies for refresh tokens
- Store refresh token server-side only
- Reduces XSS attack surface

---

## JWT Configuration

### Environment Variables

**User Authentication (Exposed Services):**
```bash
JWT_SECRET=jwt-super-secret-signing-key-change-in-production-must-be-32chars-minimum-xyz
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Service-to-Service (Internal):**
```bash
INTERNAL_JWT_SECRET=internal-service-super-secret-key-32chars-minimum-change-in-prod
INTERNAL_JWT_ALGORITHM=HS256
SERVICE_TOKEN_EXPIRE_MINUTES=15
```

**Google OAuth:**
```bash
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Important:**
- ⚠️ Change all secrets in production
- ⚠️ Use strong random strings (32+ characters)
- ⚠️ Keep INTERNAL_JWT_SECRET secure (never expose)
- ✅ Stored in `.env` file (not in repository)
- ✅ Passed to services via docker-compose environment
- ✅ Different secrets for user vs service tokens

---

## API Endpoints

### Auth Tokens Service (Port 8001)

#### Login (OAuth2 Password Flow)
```
POST /api/v1/tokens
Content-Type: application/x-www-form-urlencoded

username={email}&password={password}

Response:
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": { ... }
}
```

#### Google Login
```
POST /api/v1/auth/google/token
Content-Type: application/json

{
  "id_token": "google-id-token"
}

Response: Same as login
```

#### Token Refresh
```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "current-refresh-token"
}

Response:
{
  "access_token": "new-access-token",
  "refresh_token": "new-refresh-token",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

#### Logout
```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}

Response:
{
  "message": "Successfully logged out"
}
```

### User Management Service (Port 8010)

#### Register
```
POST /user/api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "phone_number": "+1234567890"
}

Response:
{
  "user_id": "uuid",
  "email": "user@example.com",
  "status": "pending_verification",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Document Processor (Port 8070 - Internal Only)

#### Public Endpoints (No Authentication)
```
GET /api/v1/documents/types
├─ Access: ✅ Via API Gateway (recommended)
├─ Access: 🧪 Direct from Docker network (testing)
├─ Access: ❌ NOT from host machine
├─ Authentication: ❌ Not required
└─ Returns: List of supported document types

GET /actuator/health
├─ Access: ✅ Via API Gateway
├─ Authentication: ❌ Not required
└─ Returns: Service health status
```

#### Protected Endpoints (Service JWT Required)
```
POST /api/v1/documents/process
├─ Access: ✅ Via API Gateway only
├─ Authentication: ✅ Service JWT required
└─ Returns: Processing result

POST /api/v1/documents/batch-process
├─ Access: ✅ Via API Gateway only
├─ Authentication: ✅ Service JWT required
└─ Returns: List of processing results

GET /api/v1/documents/status/{processId}
├─ Access: ✅ Via API Gateway only
├─ Authentication: ✅ Service JWT required
└─ Returns: Processing status
```

---

## Security Checklist

### Infrastructure Security
- ✅ Port 8070 not exposed in docker-compose.yml
- ✅ Internal services only accessible via Docker network
- ✅ API Gateway as single entry point
- ✅ All services in isolated Docker network

### Authentication Security
- ✅ Short-lived access tokens (30 minutes)
- ✅ Long-lived refresh tokens (7 days)
- ✅ Refresh token rotation on use
- ✅ Refresh token revocation on logout
- ✅ Database storage for refresh tokens
- ✅ Independent JWT validation in each service
- ✅ Different secrets for user vs service tokens

### Service Security
- ✅ Document Processor has SecurityConfig.java
- ✅ Public endpoints explicitly allowed in SecurityConfig
- ✅ Protected endpoints require service JWT
- ✅ JwtValidator validates service tokens
- ✅ Service tokens have short expiration (15 min)
- ✅ Service tokens never exposed to clients

### Frontend Security
- ✅ Access tokens stored in memory only
- ✅ Refresh tokens in secure storage
- ✅ Automatic token refresh on expiry
- ✅ Secure logout clears all tokens
- ✅ HTTPS enforced in production
- ✅ No sensitive data in localStorage

### Audit & Monitoring
- ✅ Complete audit trail through API Gateway
- ✅ Login/logout events logged
- ✅ Token refresh events logged
- ✅ Failed authentication attempts logged

---

## Testing Guide

### 1. Test User Registration

```bash
curl -X POST http://localhost:8010/user/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "phone_number": "+1234567890"
  }'
```

### 2. Test Login

```bash
curl -X POST http://localhost:8001/api/v1/tokens \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123!"
```

### 3. Test Token Refresh

```bash
# Save tokens from login
ACCESS_TOKEN="..."
REFRESH_TOKEN="..."

# Refresh tokens
curl -X POST http://localhost:8001/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

### 4. Test Logout

```bash
curl -X POST http://localhost:8001/api/v1/auth/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 5. Test API Gateway Access

```bash
# Access document processor via gateway
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/v1/documents/types
```

### 6. Verify Port Isolation

```bash
# This should fail (port not exposed)
curl http://localhost:8070/api/v1/documents/types
# Expected: Connection refused
```

---

## Common Issues & Solutions

### ❌ Issue: 401 Unauthorized

**Possible causes:**
1. Token expired
   - Use refresh token to get new access token
2. Invalid token signature
   - Check JWT_SECRET matches across services
3. Token not in proper format
   - Must be: `Authorization: Bearer {token}`

**Solution:**
```bash
# Refresh token
curl -X POST http://localhost:8001/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

### ❌ Issue: Connection Refused on Port 8070

**Solution:** This is correct! Port 8070 is intentionally not exposed.
Use API Gateway instead:
```bash
# ❌ Wrong
curl http://localhost:8070/api/v1/documents/types

# ✅ Correct
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/documents/types
```

### ❌ Issue: Refresh Token Invalid

**Possible causes:**
1. Token already used (rotation)
2. Token revoked (logout)
3. Token expired (7 days)

**Solution:** User must login again

### ❌ Issue: Google Sign-In Fails

**Possible causes:**
1. Invalid Google Client ID
2. ID token expired
3. ID token signature invalid

**Solution:** Check Google OAuth configuration and ensure ID token is fresh

---

## Configuration Files

**Docker Compose:**
- Location: `docker-compose.yml`
- Ports: API Gateway (8000), Auth Tokens (8001), User Management (8010)
- Networks: `am-network` (internal)

**Backend Services:**
- Auth Tokens: `am-auth-tokens/`
- User Management: `am-user-management/`
- API Gateway: `am-api-gateway/`
- Document Processor: `AM-Repos/am-document-processor/`

**Frontend:**
- Location: `AM-Repos/am-investment-ui-1/`
- Framework: Flutter
- State Management: flutter_bloc
- Auth Guide: See `frontend_auth_guide.md`

---

## Summary

✅ **Complete Authentication System:**
- User registration with email verification ✓
- Email/password login with JWT tokens ✓
- Google OAuth integration ✓
- Access/refresh token pairs ✓
- Token refresh with rotation ✓
- Secure logout with token revocation ✓
- Service-to-service authentication ✓
- Frontend integration with Flutter ✓
- Port isolation for internal services ✓
- Complete audit trail ✓

**ALWAYS use API Gateway for client access. Internal services should never be accessed directly from the host machine.**
