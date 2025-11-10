# Auth Test - Microservices Authentication System

A production-ready, microservices-based authentication system built with Clean Architecture principles, featuring JWT token management and comprehensive user management capabilities.

## 🎯 What is this Application?

**Auth Test** is a complete authentication and authorization platform designed for modern web applications. It consists of two independent microservices that work together to provide secure user management and token-based authentication:

1. **AM User Management Service** - Handles user registration, authentication, and account management
2. **AM Auth Tokens Service** - Manages JWT token creation, validation, and lifecycle

The system is designed with security, scalability, and maintainability as core principles, making it suitable for production deployments.

## 🏗️ Architecture Overview

This is a **microservices architecture** where each service has a specific responsibility:

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Application                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├─────────────────┬──────────────────────────┐
                   │                 │                          │
                   ▼                 ▼                          ▼
    ┌──────────────────────┐  ┌──────────────────┐   ┌────────────────┐
    │  Auth Tokens Service │  │ User Management  │   │   PostgreSQL   │
    │   (Port 5000/8000)   │──│  Service (8000)  │───│    Database    │
    │   JWT Operations     │  │  User Accounts   │   │   Persistence  │
    └──────────────────────┘  └──────────────────┘   └────────────────┘
```

### Service Responsibilities

#### 🔑 AM Auth Tokens Service (Port 5000)
- **Purpose**: JWT token lifecycle management
- **Key Features**:
  - Create JWT access tokens after credential validation
  - Validate JWT tokens and extract user claims
  - OAuth2-compatible token endpoints
  - Account status enforcement (only ACTIVE users get tokens)
  - Integration with User Management for credential validation
- **Technology**: FastAPI, Python 3.11

#### 👥 AM User Management Service (Port 8000)
- **Purpose**: User account management and authentication
- **Key Features**:
  - User registration with email verification
  - Secure credential validation (Bcrypt password hashing)
  - Account status management (ACTIVE, INACTIVE, SUSPENDED)
  - Email verification system
  - PostgreSQL data persistence
  - Clean Architecture with Domain-Driven Design
- **Technology**: FastAPI, PostgreSQL 15+, SQLAlchemy 2.0, Python 3.11

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (for User Management service)
- pip or uv for package management

### 1. Clone the Repository
```bash
git clone https://github.com/AM-Portfolio/auth-test.git
cd auth-test
```

### 2. Setup User Management Service
```bash
cd am/am-user-management

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL database
createdb am_user_management

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Run the service
python main_integrated.py
```
Service will be available at `http://localhost:8000`

### 3. Setup Auth Tokens Service
```bash
cd am/am-auth-tokens

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Set USER_SERVICE_URL=http://localhost:8000

# Run the service
python main.py
```
Service will be available at `http://localhost:5000`

## 📡 API Endpoints

### Auth Tokens Service (Port 5000)
- `POST /api/v1/tokens` - Create JWT access token with credentials
- `POST /api/v1/tokens/oauth` - OAuth2-compatible token endpoint
- `POST /api/v1/validate` - Validate JWT token
- `GET /health` - Health check
- `GET /api/v1/docs` - API documentation (when DEBUG=true)

### User Management Service (Port 8000)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Validate credentials and return user data
- `GET /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/resend-verification` - Resend verification email
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🔐 Authentication Flow

Here's how the services work together for a complete authentication flow:

1. **User Registration**
   - Client → User Management Service: `POST /api/v1/auth/register`
   - User account created with status="PENDING" (awaiting email verification)

2. **Email Verification**
   - User clicks verification link
   - Client → User Management Service: `GET /api/v1/auth/verify-email?token=...`
   - User status updated to "ACTIVE"

3. **Token Creation (Login)**
   - Client → Auth Tokens Service: `POST /api/v1/tokens` (username + password)
   - Auth Tokens → User Management: `POST /api/v1/auth/login` (validate credentials)
   - User Management validates and returns user data including status
   - Auth Tokens checks status == "ACTIVE"
   - If active, JWT token is created and returned to client

4. **Token Usage**
   - Client → Any Service: API request with `Authorization: Bearer <token>`
   - Service validates token (internal validation or via Auth Tokens Service)

## 🛡️ Security Features

### Password Security
- Bcrypt hashing with configurable rounds (default: 12)
- No plain-text password storage
- Secure password validation

### Account Status Enforcement
- Only ACTIVE users can obtain JWT tokens
- Status validation prevents unauthorized access
- Missing status treated as security failure (403 Forbidden)

### Token Security
- JWT tokens with configurable expiration (default: 24 hours)
- HS256 algorithm for token signing
- Configurable JWT secret for production security

### Input Validation
- Pydantic schemas for all API inputs
- SQL injection prevention via ORM
- CORS configuration for cross-origin requests

## 📁 Project Structure

```
auth-test/
├── am/
│   ├── am-user-management/          # User Management microservice
│   │   ├── core/                    # Domain kernel (value objects, interfaces)
│   │   ├── modules/                 # Feature modules (account management)
│   │   ├── shared_infra/            # Infrastructure (database, events)
│   │   ├── main_integrated.py       # FastAPI application entry point
│   │   ├── requirements.txt         # Python dependencies
│   │   └── README.md               # Service-specific documentation
│   │
│   └── am-auth-tokens/             # Auth Tokens microservice
│       ├── app/
│       │   ├── core/               # JWT security operations
│       │   ├── api/v1/             # API endpoints
│       │   └── services/           # User validation integration
│       ├── shared_infra/           # Configuration management
│       ├── main.py                 # FastAPI application entry point
│       ├── requirements.txt        # Python dependencies
│       └── README.md              # Service-specific documentation
│
├── pyproject.toml                  # Project metadata
└── README.md                       # This file
```

## 🧪 Testing

### User Management Service
```bash
cd am/am-user-management
python -m pytest
```

### Auth Tokens Service
```bash
cd am/am-auth-tokens
pytest
```

### Manual Testing with curl

**Register a user:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Create token (after email verification):**
```bash
curl -X POST "http://localhost:5000/api/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "securepass123"
  }'
```

## 🚢 Production Deployment

### Environment Configuration

Both services use environment variables for configuration. Key variables:

**User Management Service:**
- `DATABASE_URL` - PostgreSQL connection string
- `BCRYPT_ROUNDS` - Password hashing strength (default: 12)
- `REQUIRE_EMAIL_VERIFICATION` - Enable/disable email verification

**Auth Tokens Service:**
- `JWT_SECRET` - Secret key for JWT signing (MUST be changed in production)
- `JWT_EXPIRE_MINUTES` - Token expiration time (default: 1440)
- `USER_SERVICE_URL` - URL of User Management service

### Docker Support

Both services include Docker support. See individual service READMEs for Docker Compose configurations.

## 📚 Documentation

- **User Management**: See `am/am-user-management/README.md` and `PRODUCTION_GUIDE.md`
- **Auth Tokens**: See `am/am-auth-tokens/README.md` and `ENVIRONMENT_GUIDE.md`
- **Replit Setup**: See `replit.md` for cloud development environment setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 Recent Updates

- **2025-10-06**: Security hardening and integration fixes
  - Fixed circular dependency between services
  - Added account status validation
  - Improved security for inactive/suspended accounts

- **2025-10-04**: Initial Replit setup
  - Python 3.11 environment
  - FastAPI dependencies installed
  - Development workflow configured

## 🆘 Support

- **Issues**: Open an issue on GitHub for bug reports or feature requests
- **Documentation**: Check service-specific README files for detailed information
- **Community**: Use GitHub Discussions for questions and community support

## 📄 License

This project is part of the AM Portfolio and is available under the MIT License.

---

**Built with ❤️ by the AM Portfolio team**
