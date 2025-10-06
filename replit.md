# Auth Tokens Microservice - Replit Setup

## Overview
FastAPI-based JWT authentication service that handles token creation and validation. This is a backend API service that integrates with a separate user management service for secure authentication.

## Project Architecture
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn with auto-reload
- **Language**: Python 3.11
- **Services**:
  - Auth Tokens API: Port 5000
  - User Management API: Port 8000

## Key Features
- JWT token creation and validation
- User credential validation via User Management service
- Account status security enforcement
- RESTful API endpoints
- Health monitoring
- CORS support

## API Endpoints
### Auth Tokens Service (Port 5000)
- `GET /` - Service information
- `GET /health` - Health check
- `GET /info` - Detailed service info
- `POST /api/v1/tokens` - Create access token
- `POST /api/v1/tokens/oauth` - OAuth2-compatible token endpoint
- `POST /api/v1/validate` - Validate JWT token
- API documentation at `/api/v1/docs` (when DEBUG=true)

### User Management Service (Port 8000)
- `POST /api/v1/auth/login` - Validate credentials and return user data

## Configuration
Environment variables are managed in `.env`:
- `PORT=5000` - Auth Tokens service port (Replit standard)
- `HOST=0.0.0.0` - Bind to all interfaces
- `DEBUG=true` - Enable debug mode and API docs
- `JWT_SECRET` - Secret key for JWT signing
- `USER_SERVICE_URL=http://localhost:8000` - User Management service URL

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
