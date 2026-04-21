# 🔐 AM User Management

A production-ready user management system built with \*\*Clean Ar# Run tests
python -m pytest

# Test API endpoints

python tests/api/test_integrated_api.py

# Test with curlure\*\* principles, featuring secure authentication, email verification, and PostgreSQL integration.

## 🚀 **Current Status: FULLY FUNCTIONAL**

✅ **Complete Clean Architecture Implementation**  
✅ **PostgreSQL Database Integration**  
✅ **User Registration & Authentication**  
✅ **Bcrypt Password Hashing**  
✅ **Domain-Driven Design**  
✅ **Comprehensive Logging & Error Handling**

## 📋 **Features**

- **🔒 Secure Authentication**: Bcrypt password hashing with configurable rounds
- **📧 Email Verification**: Token-based email verification system (production-ready templates included)
- **🗄️ PostgreSQL Database**: Async SQLAlchemy with connection pooling
- **🏗️ Clean Architecture**: Modular design with clear separation of concerns
- **🔄 Domain Events**: Event-driven architecture with mock event bus
- **⚡ FastAPI Integration**: High-performance async API with automatic OpenAPI documentation
- **📊 Comprehensive Logging**: Structured JSON logging with request tracking
- **🧪 Full Test Coverage**: Unit and integration tests with real database testing

## 🛠️ **Tech Stack**

- **Framework**: FastAPI 0.104.1+ with async support
- **Database**: PostgreSQL 15+ with asyncpg driver
- **ORM**: SQLAlchemy 2.0+ with async sessions
- **Authentication**: Bcrypt password hashing
- **Validation**: Pydantic v2 with custom value objects
- **Architecture**: Clean Architecture with Domain-Driven Design

## 🚀 **Quick Start**

### Prerequisites

- Python 3.9+
- PostgreSQL 15+
- pip or poetry

### 1. Clone & Setup

```bash
git clone https://github.com/AM-Portfolio/am-user-management.git
cd am-user-management
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb am_user_management
```

### 3. Environment Configuration

```bash
# Create .env file
cp .env.example .env

# Update .env with your PostgreSQL credentials
DATABASE_URL=postgresql+asyncpg://your_username@localhost:5432/am_user_management
```

### 4. Run Application

```bash
python3 main_integrated.py
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

## 📡 **API Endpoints**

### Authentication

- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Authenticate user
- `GET /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/resend-verification` - Resend verification email

### System

- `GET /health` - Health check endpoint
- `GET /api/v1/auth/status` - Authentication system status

## 🧪 **Testing**

```bash
# Run all tests
python -m pytest

# Test specific functionality
python debug_login_process.py

# Test with curl
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secure123", "first_name": "Test", "last_name": "User"}'
```

## 📁 **Project Structure**

```
am-user-management/
├── core/                           # Domain kernel
│   ├── value_objects/             # Email, UserId, PhoneNumber
│   └── interfaces/                # Repository & EventBus abstractions
│
├── modules/
│   └── account_management/        # 🔐 User authentication module
│       ├── api/public/           # FastAPI routes & schemas
│       ├── application/          # Use cases & services
│       ├── domain/              # Business logic & entities
│       └── infrastructure/      # Database & external services
│
├── shared_infra/                  # Technical infrastructure
│   ├── database/                 # PostgreSQL configuration
│   ├── events/                   # Event bus implementation
│   └── config/                   # Settings & feature flags
│
├── main_integrated.py            # Production FastAPI application
├── PRODUCTION_GUIDE.md          # 📚 Production implementation guide
└── requirements.txt              # Dependencies
```

## 🔐 **Security Features**

- **Password Security**: Bcrypt with 12 rounds (configurable)
- **Email Verification**: Required before login (configurable)
- **Input Validation**: Pydantic schemas with custom validators
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Error Handling**: Secure error messages without sensitive data exposure

## 📈 **Production Readiness**

This system is designed for production use with:

- **Scalable Architecture**: Clean separation enables easy testing and modification
- **Database Migrations**: SQLAlchemy-based schema management
- **Monitoring Ready**: Structured logging and health checks
- **Docker Support**: Containerization ready
- **Environment Configuration**: 12-factor app compliance

For detailed production deployment instructions, see [**PRODUCTION_GUIDE.md**](./PRODUCTION_GUIDE.md).

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: See [PRODUCTION_GUIDE.md](./PRODUCTION_GUIDE.md) for comprehensive implementation guidance
- **Issues**: Open an issue on GitHub for bug reports or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support

---

**Built with ❤️ by the AM Portfolio team**

# am-user-management
