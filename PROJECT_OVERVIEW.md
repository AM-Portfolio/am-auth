# Authentication System - Project Overview

## What This Application Is About

This is a **microservices-based authentication and user management system** built with Python/FastAPI. It provides secure user authentication, JWT token management, and Google OAuth integration.

## Architecture

The system consists of **2 main microservices**:

### 1. **AM User Management Service** (Port 8000)
**Purpose:** Manages user accounts, registration, and authentication

**Key Features:**
- ✅ User registration with email and password
- ✅ User login with credential validation
- ✅ Password hashing (bcrypt) for security
- ✅ Email verification workflow
- ✅ User status management (ACTIVE, PENDING_VERIFICATION, SUSPENDED, DELETED)
- ✅ Google OAuth user creation and linking
- ✅ PostgreSQL database for user data persistence
- ✅ Domain-driven design architecture
- ✅ Event-driven architecture with domain events

**Database Schema:**
- User accounts with email, password, phone number
- Google OAuth integration (google_id, profile_picture_url)
- User status tracking
- Email verification status
- Last login timestamps

### 2. **AM Auth Tokens Service** (Port 8080)
**Purpose:** Generates and validates JWT tokens for authenticated users

**Key Features:**
- ✅ JWT token creation for authenticated users
- ✅ Token validation and verification
- ✅ Google OAuth token validation
- ✅ Service-to-service authentication
- ✅ Token expiration management
- ✅ User status verification before issuing tokens
- ✅ Mock Google token generation for testing

## How It Works

### Standard Authentication Flow:
```
1. User registers → AM User Management (creates account)
2. User verifies email → Account status becomes ACTIVE
3. User logs in → AM User Management (validates credentials)
4. System creates JWT → AM Auth Tokens (generates token)
5. User makes requests → Uses JWT token for authentication
6. System validates token → AM Auth Tokens (verifies token)
```

### Google OAuth Flow:
```
1. User signs in with Google → Gets Google ID token
2. System validates Google token → AM Auth Tokens
3. System creates/links user → AM User Management
4. System issues JWT token → AM Auth Tokens
5. User authenticated → Can access protected resources
```

## Technology Stack

### Backend Framework:
- **FastAPI** - Modern Python web framework
- **Python 3.11+** - Programming language
- **Uvicorn** - ASGI server

### Database:
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **Alembic** - Database migrations

### Security:
- **bcrypt** - Password hashing
- **python-jose** - JWT token handling
- **google-auth** - Google OAuth validation
- **passlib** - Password utilities

### Architecture Patterns:
- **Microservices** - Separate services for different concerns
- **Domain-Driven Design (DDD)** - Business logic organization
- **Clean Architecture** - Separation of concerns
- **Event-Driven** - Domain events for cross-module communication
- **Repository Pattern** - Data access abstraction

### Development Tools:
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Postman** - API testing
- **pytest** - Unit testing

## Project Structure

```
auth-test-3/
├── am/
│   ├── am-auth-tokens/          # JWT Token Service (Port 8080)
│   │   ├── app/
│   │   │   ├── api/v1/          # API endpoints
│   │   │   ├── core/            # Security & JWT logic
│   │   │   ├── database/        # Database models
│   │   │   └── services/        # Business logic
│   │   └── shared_infra/        # Shared configuration
│   │
│   ├── am-user-management/      # User Management Service (Port 8000)
│   │   ├── modules/
│   │   │   └── account_management/  # Main module
│   │   │       ├── api/         # API routers
│   │   │       ├── application/ # Use cases
│   │   │       ├── domain/      # Business entities
│   │   │       └── infrastructure/ # Database & external services
│   │   ├── core/                # Value objects
│   │   ├── shared_infra/        # Database, events, logging
│   │   └── tests/               # Test suite
│   │
│   └── docker-compose.yml       # Container orchestration
│
├── postman/                     # API testing collections
└── Documentation files (.md)
```

## Current Implementation Status

### ✅ Fully Implemented:
1. User registration with validation
2. User login with password verification
3. JWT token generation and validation
4. Google OAuth integration
5. Internal service-to-service APIs
6. Database persistence (PostgreSQL)
7. Password hashing and security
8. User status management
9. Health check endpoints
10. Comprehensive API documentation

### 🚧 Partially Implemented:
1. Email verification (endpoint exists, needs token storage)
2. Password reset (sends email, needs token validation)
3. User logout (mock implementation)

### ❌ Not Implemented (Empty Placeholders):
1. Permissions & Roles module
2. Subscription management module
3. User profile management module
4. Token refresh mechanism
5. Rate limiting
6. Account deletion

## Use Cases

### For Developers:
- Build applications that need user authentication
- Integrate Google Sign-In
- Manage user accounts and permissions
- Issue and validate JWT tokens

### For Applications:
- Mobile apps needing user authentication
- Web applications with login systems
- APIs requiring secure access control
- Multi-tenant SaaS platforms

### For Businesses:
- User identity management
- Secure authentication infrastructure
- OAuth provider integration
- Compliance with security standards

## API Endpoints

### User Management Service (Port 8000):
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/password-reset` - Request password reset
- `GET /api/v1/auth/verify-email` - Verify email (stub)
- `POST /api/v1/auth/logout` - User logout (stub)
- `POST /api/v1/google/auth` - Google OAuth user creation
- `GET /internal/v1/users/{user_id}` - Internal user lookup
- `GET /health` - Health check

### Auth Tokens Service (Port 8080):
- `POST /api/v1/tokens` - Create JWT token
- `POST /api/v1/tokens/by-user-id` - Create token by user ID
- `POST /api/v1/tokens/oauth` - OAuth2 token endpoint
- `POST /api/v1/validate` - Validate JWT token
- `POST /api/v1/auth/google/token` - Google OAuth authentication
- `POST /test/mock/google/token` - Generate mock Google token (testing)
- `GET /health` - Health check

## Security Features

1. **Password Security:**
   - Bcrypt hashing with salt
   - Minimum password requirements
   - Secure password storage

2. **Token Security:**
   - JWT with expiration
   - Signature verification
   - User status validation

3. **OAuth Security:**
   - Google token signature verification
   - Audience validation
   - Issuer verification

4. **Account Security:**
   - Email verification requirement
   - Account status enforcement
   - Audit logging (last login tracking)

## Testing

### Available Test Tools:
- Postman collections for all endpoints
- Mock Google OAuth service for testing
- Health check endpoints
- Comprehensive API documentation
- cURL examples in documentation

### Test Scenarios:
- User registration flow
- Login with valid/invalid credentials
- Email verification workflow
- Google OAuth integration
- JWT token validation
- Error handling and edge cases

## Deployment

### Local Development:
```bash
# Start User Management Service
cd am/am-user-management
uvicorn main:app --reload --port 8000

# Start Auth Tokens Service
cd am/am-auth-tokens
uvicorn main:app --reload --port 8080
```

### Docker Deployment:
```bash
cd am
docker-compose up -d
```

### Database Setup:
```bash
# Create PostgreSQL database
createdb am_user_management

# Database migrations handled automatically on startup
```

## Key Benefits

1. **Microservices Architecture** - Scalable and maintainable
2. **Security First** - Industry-standard security practices
3. **OAuth Integration** - Easy Google Sign-In
4. **Clean Code** - Domain-driven design principles
5. **Well Documented** - Comprehensive API documentation
6. **Test Ready** - Postman collections and mock services
7. **Production Ready** - Docker containerization

## Future Enhancements

1. Complete email verification implementation
2. Add more OAuth providers (Facebook, GitHub)
3. Implement role-based access control (RBAC)
4. Add subscription management
5. Implement rate limiting
6. Add refresh token mechanism
7. Build admin dashboard
8. Add analytics and monitoring

## Summary

This is a **professional-grade authentication system** that provides:
- Secure user registration and login
- JWT token management
- Google OAuth integration
- Microservices architecture
- Production-ready infrastructure

It's designed to be the authentication backbone for modern web and mobile applications, with clean architecture, comprehensive security, and easy integration.
