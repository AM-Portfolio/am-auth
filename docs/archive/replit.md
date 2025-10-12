# Auth Tokens Microservice - Replit Setup

## Overview
FastAPI-based JWT authentication service that handles token creation and validation. This is a backend API service that integrates with a separate user management service for secure authentication.

## Project Architecture
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn with auto-reload
- **Language**: Python 3.11
- **Services**:
  - Auth Tokens API: Port 8080 (updated from 5000)
  - User Management API: Port 8000

## Key Features
- JWT token creation and validation
- User credential validation via User Management service
- **Google OAuth 2.0 authentication** (NEW)
- Account status security enforcement
- RESTful API endpoints
- Health monitoring
- CORS support
- Mock token generation for testing

## API Endpoints
### Auth Tokens Service (Port 8080)
- `GET /` - Service information
- `GET /health` - Health check
- `GET /info` - Detailed service info
- `POST /api/v1/tokens` - Create access token
- `POST /api/v1/tokens/oauth` - OAuth2-compatible token endpoint
- `POST /api/v1/validate` - Validate JWT token
- **`POST /api/v1/auth/google/token`** - Google OAuth authentication (NEW)
- **`POST /test/mock/google/token`** - Generate mock Google tokens for testing (NEW)
- API documentation at `/api/v1/docs` (when DEBUG=true)

### User Management Service (Port 8000)
- `POST /api/v1/auth/login` - Validate credentials and return user data
- **`POST /api/v1/google/auth`** - Create/link Google OAuth users (NEW)

## Configuration
Environment variables are managed in `.env`:
- `PORT=8080` - Auth Tokens service port (updated from 5000)
- `HOST=0.0.0.0` - Bind to all interfaces
- `DEBUG=true` - Enable debug mode and API docs
- `JWT_SECRET` - Secret key for JWT signing
- `USER_SERVICE_URL=http://localhost:8000` - User Management service URL

### Google OAuth Configuration (NEW)
- `GOOGLE_CLIENT_ID` - Google OAuth 2.0 client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth 2.0 client secret
- `GOOGLE_JWKS_URL` - Google's public key URL (default: https://www.googleapis.com/oauth2/v3/certs)
- `GOOGLE_ISSUER` - Google token issuer (default: https://accounts.google.com)
- `GOOGLE_AUTH_ENABLED` - Enable/disable Google auth (default: true)

## Security Features
### Account Status Enforcement
- Auth Tokens service validates user status before issuing JWT tokens
- Only users with status="ACTIVE" receive tokens
- Missing status is treated as security failure (403 Forbidden)
- Prevents inactive, suspended, or deleted users from authenticating

### Integration Flow
1. Client sends credentials to Auth Tokens POST /api/v1/tokens
2. Auth Tokens validates credentials with User Management POST /api/v1/auth/login
3. User Management returns: {user_id, username, email, status, scopes}
4. Auth Tokens checks status == "ACTIVE" before creating JWT
5. Auth Tokens returns JWT token to client if status is valid

## Dependencies
This service requires:
- External User Management service for credential validation
- PostgreSQL database (configured in User Management service)
- Service URL configured via `USER_SERVICE_URL` environment variable

## Recent Changes
- 2025-10-09: Google OAuth 2.0 Implementation
  - Installed google-auth (v2.28.1) and requests (v2.31.0) libraries
  - Extended database schema with Google OAuth fields (google_id, auth_provider, profile_picture_url, email_verified, provider_data, last_google_login)
  - Implemented POST /api/v1/auth/google/token for Google authentication
  - Created mock Google token service for testing without real credentials
  - Built Google user creation/linking in User Management service
  - Added POST /test/mock/google/token for generating test tokens
  - Configured GOOGLE_CLIENT_ID environment variable
  - Updated port from 5000 to 8080 for Auth Tokens service
  - See GOOGLE_OAUTH_STATUS.md for complete implementation details

- 2025-10-06: Security hardening and integration fixes
  - Fixed circular dependency (User Management no longer calls Auth Tokens)
  - Added account status validation (only ACTIVE users get tokens)
  - Treats missing status as security failure to prevent bypass
  - Both /tokens and /tokens/oauth endpoints enforce status check
  - Updated UserValidationResponse to include status field
  
- 2025-10-04: Initial Replit setup
  - Installed Python 3.11
  - Installed all FastAPI dependencies
  - Configured port 5000 for Replit
  - Set up development workflow

## Google OAuth Documentation
For complete Google OAuth implementation details, testing guide, and production setup, see:
- **GOOGLE_OAUTH_STATUS.md** - Complete implementation status and usage guide
- **GOOGLE_OAUTH_IMPLEMENTATION.md** - Original specification and requirements
