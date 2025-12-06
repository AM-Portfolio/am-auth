# Complete Environment Variables Inventory

## Overview
This document tracks ALL environment variables across the AM Authentication system, their purposes, locations, and usage.

---

## 1. JWT & Security Variables

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `JWT_SECRET` | jwt-super-secret-... (32+ chars) | `.env.docker` | Signs user authentication tokens | API Gateway, Auth Tokens, User Management | **CRITICAL** |
| `INTERNAL_JWT_SECRET` | internal-service-super-secret-... (32+ chars) | `.env.docker` | Signs service-to-service tokens | Python Service, Java Service | **CRITICAL** |
| `JWT_ALGORITHM` | HS256 | `docker-compose.yml` | Algorithm for token signing | API Gateway, Auth Tokens | Standard |
| `SECRET_KEY` | am-user-management-super-secret-... | `.env.docker` | Application secret for sessions | User Management | Standard |

**Location Map:**
- `.env.docker` - Main secrets file (encrypted in production)
- `docker-compose.yml` - References via `${JWT_SECRET}`, `${INTERNAL_JWT_SECRET}`

---

## 2. Database Variables

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `DATABASE_URL` | postgresql://postgres:password@host.docker.internal:5432/postgres | `.env.docker` | PostgreSQL connection string | Auth Tokens | **CRITICAL** |
| `DB_HOST` | host.docker.internal | `.env.docker` | Database host | Database clients | Standard |
| `DB_PORT` | 5432 | `.env.docker` | Database port | Database clients | Standard |
| `DB_NAME` | postgres | `.env.docker` | Database name | Database clients | Standard |
| `DB_USER` | postgres | `.env.docker` | Database username | Database clients | Standard |
| `DB_PASSWORD` | password | `.env.docker` | Database password | Database clients | **SENSITIVE** |
| `DB_ECHO` | false | `.env.docker` | SQL logging | SQLAlchemy ORM | Debug |
| `DB_POOL_SIZE` | 5 | `.env.docker` | Connection pool size | Database clients | Tuning |
| `DB_MAX_OVERFLOW` | 10 | `.env.docker` | Max overflow connections | Database clients | Tuning |
| `DB_POOL_TIMEOUT` | 30 | `.env.docker` | Pool timeout seconds | Database clients | Tuning |
| `POSTGRES_PASSWORD` | postgres | `.env.docker` | PostgreSQL root password | Docker Compose | **SENSITIVE** |
| `POSTGRES_USERNAME` | password | `.env.docker` | PostgreSQL username | Docker Compose | Standard |
| `POSTGRES_URL` | postgresql://postgres:password@host.docker.internal:5432/postgres | `.env.docker` | Full connection URL | Backup/reference | Standard |
| `POSTGRES_DATABASE` | postgres | `.env.docker` | Default database | Docker Compose | Standard |

**Location Map:**
- `.env.docker` - All database configuration
- `docker-compose.yml` - References via `${DATABASE_URL}`
- Used by: `auth-tokens` service, `am-user-management` service

---

## 3. Service URL Variables (From config/services.env)

### Service URLs - Dynamic Construction
| Variable | HTTP Example | HTTPS Example | Location | Purpose | Used By |
|----------|--------------|---------------|----------|---------|---------|
| `AUTH_SERVICE_URL` | http://auth-tokens:8001 | https://auth-tokens | `config/services.env` | Auth service endpoint | API Gateway, User Management |
| `USER_MANAGEMENT_URL` | http://am-user-management:8000 | https://am-user-management | `config/services.env` | User service endpoint | API Gateway, Auth Tokens |
| `PYTHON_SERVICE_URL` | http://am-python-internal-service:8002 | https://am-python-internal-service | `config/services.env` | Python internal service | API Gateway |
| `JAVA_SERVICE_URL` | http://am-java-internal-service:8003 | https://am-java-internal-service | `config/services.env` | Java internal service | API Gateway |
| `DOCUMENT_PROCESSOR_URL` | http://am-document-processor:8070 | https://am-document-processor | `config/services.env` | Document processor service | API Gateway |
| `PORTFOLIO_URL` | http://am-portfolio:8080 | https://am-portfolio | `config/services.env` | Portfolio service | API Gateway |
| `TRADE_API_URL` | http://am-trade-api:8073 | https://am-trade-api | `config/services.env` | Trade API service | API Gateway |
| `MARKET_DATA_URL` | http://am-market-data:8092 | https://am-market-data | `config/services.env` | Market data service | API Gateway |

### Service Host & Port Variables (Used to construct URLs)
| Variable | Value | Location | Purpose | Depends On |
|----------|-------|----------|---------|-----------|
| `SERVICE_PROTOCOL` | http | `config/services.env` | Protocol prefix | - |
| `USE_HTTPS` | false | `config/services.env` | Flag for HTTPS mode | - |
| `AUTH_TOKENS_SERVICE_HOST` | auth-tokens | `config/services.env` | Service hostname | - |
| `AUTH_TOKENS_SERVICE_PORT` | 8001 | `config/services.env` | Service port | - |
| `USER_MANAGEMENT_SERVICE_HOST` | am-user-management | `config/services.env` | Service hostname | - |
| `USER_MANAGEMENT_SERVICE_PORT` | 8000 | `config/services.env` | Service port | - |
| `PYTHON_INTERNAL_SERVICE_HOST` | am-python-internal-service | `config/services.env` | Service hostname | - |
| `PYTHON_INTERNAL_SERVICE_PORT` | 8002 | `config/services.env` | Service port | - |
| `JAVA_INTERNAL_SERVICE_HOST` | am-java-internal-service | `config/services.env` | Service hostname | - |
| `JAVA_INTERNAL_SERVICE_PORT` | 8003 | `config/services.env` | Service port | - |
| `DOCUMENT_PROCESSOR_SERVICE_HOST` | am-document-processor | `config/services.env` | Service hostname | - |
| `DOCUMENT_PROCESSOR_SERVICE_PORT` | 8070 | `config/services.env` | Service port | - |
| `PORTFOLIO_SERVICE_HOST` | am-portfolio | `config/services.env` | Service hostname | - |
| `PORTFOLIO_SERVICE_PORT` | 8080 | `config/services.env` | Service port | - |
| `TRADE_API_SERVICE_HOST` | am-trade-api | `config/services.env` | Service hostname | - |
| `TRADE_API_SERVICE_PORT` | 8073 | `config/services.env` | Service port | - |
| `MARKET_DATA_SERVICE_HOST` | am-market-data | `config/services.env` | Service hostname | - |
| `MARKET_DATA_SERVICE_PORT` | 8092 | `config/services.env` | Service port | - |

**How URLs Are Constructed:**
```
AUTH_SERVICE_URL = ${SERVICE_PROTOCOL}://${AUTH_TOKENS_SERVICE_HOST}:${AUTH_TOKENS_SERVICE_PORT}
                 = http://auth-tokens:8001  (HTTP mode)
                 = https://auth-tokens:8001 (can be modified)
```

**To Switch HTTP ↔ HTTPS:**
1. Edit `config/services.env`
2. Change `SERVICE_PROTOCOL=https` (removes port visually in URLs)
3. Restart: `docker-compose up -d`

---

## 4. Redis Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `REDIS_HOSTNAME` | host.docker.internal | `.env.docker` | Redis host | Market Data, Services | Standard |
| `REDIS_PASSWORD` | RedisPassword123! | `.env.docker` | Redis password | Redis clients | **SENSITIVE** |
| `REDIS_PORT` | 6379 | `.env.docker` | Redis port | Redis clients | Standard |
| `REDIS_URL` | redis://:RedisPassword123!@host.docker.internal:6379/0 | `.env.docker` | Full connection URL | Clients | Standard |
| `REDIS_MAX_CONNECTIONS` | 10 | `.env.docker` | Max connections | Connection pooling | Tuning |

---

## 5. MongoDB & Kafka (External Services)

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `MONGODB_URL` | mongodb://host.docker.internal:27017/portfolio?authSource=admin | `.env.docker` | MongoDB connection | Document Processor, Portfolio, Trade, Market Data | **CRITICAL** |
| `KAFKA_BOOTSTRAP_SERVERS` | host.docker.internal:9092 | `.env.docker` | Kafka bootstrap servers | Microservices | **CRITICAL** |
| `KAFKA_SECURITY_PROTOCOL` | PLAINTEXT | `.env.docker` | Kafka security protocol | Kafka clients | Standard |
| `KAFKA_SASL_MECHANISM` | PLAIN | `.env.docker` | SASL mechanism | Kafka clients | Standard |
| `KAFKA_SASL_JAAS_CONFIG` | (empty) | `.env.docker` | JAAS configuration | Kafka clients | Optional |

---

## 6. Application Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `ENVIRONMENT` | docker | `.env.docker` | Deployment environment | All services | Standard |
| `DEBUG` | true | `.env.docker` | Debug mode | User Management | Debug |
| `LOG_LEVEL` | INFO | `.env.docker` | Logging level | All services | Standard |
| `LOG_FORMAT` | json | `.env.docker` | Log output format | Logging system | Standard |
| `LOG_CONSOLE` | true | `.env.docker` | Log to console | Logging system | Standard |
| `USER_MGMT_LOG_LEVEL` | INFO | `docker-compose.yml` | User service log level | User Management | Standard |
| `AUTH_TOKENS_LOG_LEVEL` | INFO | `docker-compose.yml` | Auth service log level | Auth Tokens | Standard |
| `INTERNAL_SERVICE_LOG_LEVEL` | INFO | `docker-compose.yml` | Internal service log level | Python/Java Services | Standard |
| `TITLE` | AM User Management API | `.env.docker` | API title | Documentation | Standard |
| `DESCRIPTION` | User management system with modular architecture | `.env.docker` | API description | Documentation | Standard |
| `VERSION` | 0.1.0 | `.env.docker` | API version | Documentation | Standard |

---

## 7. CORS Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `ALLOWED_ORIGINS` | * | `.env.docker` | CORS allowed origins | API Gateway | Standard |
| `ALLOWED_METHODS` | * | `.env.docker` | CORS allowed methods | API Gateway | Standard |
| `ALLOWED_HEADERS` | * | `.env.docker` | CORS allowed headers | API Gateway | Standard |

---

## 8. Email Service Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `EMAIL_SERVICE_ENABLED` | false | `.env.docker` | Enable email service | User Management | Standard |
| `ENABLE_MOCK_EMAIL` | true | `.env.docker` | Use mock email (dev) | User Management | Standard |
| `ENABLE_EMAIL_VERIFICATION` | false | `docker-compose.yml` | Email verification | User Management | Standard |
| `SMTP_HOST` | smtp.gmail.com | `.env.docker` | SMTP server | Email service | Standard |
| `SMTP_PORT` | 587 | `.env.docker` | SMTP port | Email service | Standard |
| `SMTP_USERNAME` | (empty) | `.env.docker` | SMTP username | Email service | **SENSITIVE** |
| `SMTP_PASSWORD` | (empty) | `.env.docker` | SMTP password | Email service | **SENSITIVE** |
| `SMTP_USE_TLS` | true | `.env.docker` | Use TLS | Email service | Standard |

---

## 9. User Management Policy Variables

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `PASSWORD_REQUIRE_UPPERCASE` | true | `.env.docker` | Require uppercase | Password policy | Standard |
| `PASSWORD_REQUIRE_LOWERCASE` | true | `.env.docker` | Require lowercase | Password policy | Standard |
| `PASSWORD_REQUIRE_NUMBERS` | true | `.env.docker` | Require numbers | Password policy | Standard |
| `PASSWORD_REQUIRE_SPECIAL` | true | `.env.docker` | Require special chars | Password policy | Standard |
| `EMAIL_VERIFICATION_ENABLED` | true | `.env.docker` | Email verification | User Management | Standard |
| `EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS` | 24 | `.env.docker` | Token expiry | Verification | Standard |
| `MAX_LOGIN_ATTEMPTS` | 5 | `.env.docker` | Max failed attempts | Security | Standard |
| `ACCOUNT_LOCKOUT_MINUTES` | 15 | `.env.docker` | Lockout duration | Security | Standard |
| `PASSWORD_RESET_TOKEN_EXPIRY_HOURS` | 1 | `.env.docker` | Reset token validity | Security | Standard |
| `ALLOW_REGISTRATION` | true | `.env.docker` | Allow new users | User Management | Standard |
| `REQUIRE_PHONE_VERIFICATION` | false | `.env.docker` | Phone verification | User Management | Standard |

---

## 10. Subscription & Profile Settings

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `TRIAL_DAYS` | 14 | `.env.docker` | Free trial duration | Subscription | Business |
| `DEFAULT_CURRENCY` | USD | `.env.docker` | Default currency | Billing | Business |
| `AUTO_RENEW_ENABLED` | true | `.env.docker` | Auto renewal | Subscription | Business |
| `MAX_BIO_LENGTH` | 500 | `.env.docker` | Max bio characters | Profile | Standard |
| `ALLOWED_PICTURE_FORMATS` | jpg,png,jpeg | `.env.docker` | Allowed image formats | Profile | Standard |
| `DEFAULT_ROLE` | viewer | `.env.docker` | Default user role | Permissions | Standard |

---

## 11. Logging Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `LOG_FILE_PATH` | (empty) | `.env.docker` | Log file path | Logging | Standard |
| `LOG_MAX_FILE_SIZE` | 10485760 | `.env.docker` | Max file size (10MB) | Log rotation | Standard |
| `LOG_BACKUP_COUNT` | 5 | `.env.docker` | Backup log files | Log rotation | Standard |

---

## 12. Service-Specific Settings

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `USER_MANAGEMENT_MAX_RETRIES` | 3 | `.env.docker` | Max retry attempts | User Service | Tuning |
| `USER_MANAGEMENT_RETRY_DELAY_MS` | 1000 | `.env.docker` | Retry delay (ms) | User Service | Tuning |
| `USER_MANAGEMENT_THREAD_POOL_SIZE` | 5 | `.env.docker` | Thread pool size | User Service | Tuning |
| `USER_MANAGEMENT_THREAD_QUEUE_CAPACITY` | 10 | `.env.docker` | Queue capacity | User Service | Tuning |
| `USER_MANAGEMENT_SESSION_TIMEOUT_MINUTES` | 30 | `.env.docker` | Session timeout | User Service | Standard |

---

## 13. Authentication Service Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `AUTH_TOKENS_URL` | http://host.docker.internal:8001 | `.env.docker` | Auth service URL (legacy) | Services | Standard |
| `USER_SERVICE_URL` | http://host.docker.internal:8000 | `.env.docker` | User service URL (legacy) | Services | Standard |
| `JWT_EXPIRATION_MINUTES` | 1440 | `.env.docker` | Token expiry (24 hours) | Auth | Standard |

---

## 14. Google OAuth Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `GOOGLE_CLIENT_ID` | 536930944518-v4406qrrj4o2pk594g2rc3sk6lfinlf6.apps.googleusercontent.com | `.env.docker` | OAuth client ID | Auth Tokens | **SENSITIVE** |
| `GOOGLE_CLIENT_SECRET` | (empty) | `.env.docker` | OAuth client secret | Auth Tokens | **SENSITIVE** |
| `GOOGLE_AUTH_ENABLED` | true | `.env.docker` | Enable OAuth | Auth Tokens | Standard |

---

## 15. Rate Limiting Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `RATE_LIMIT_REQUESTS` | 100 | `docker-compose.yml` | Requests per window | API Gateway | Standard |
| `RATE_LIMIT_WINDOW` | 60 | `docker-compose.yml` | Window in seconds | API Gateway | Standard |

---

## 16. Timeout Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `DEFAULT_TIMEOUT` | 30.0 | `docker-compose.yml` | Default timeout (seconds) | API Gateway | Standard |
| `LONG_TIMEOUT` | 60.0 | `docker-compose.yml` | Long timeout (seconds) | API Gateway | Standard |

---

## 17. Build Context Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `AM_REPO_PATH` | A:\InfraCode\AM-Portfolio | `.env.docker` | Base repository path | Docker build | **CRITICAL** |
| `DOCUMENT_PROCESSOR_CONTEXT` | ${AM_REPO_PATH}\am-document-processor | `.env.docker` | Build context path | Docker build | Standard |
| `PORTFOLIO_CONTEXT` | ${AM_REPO_PATH}\am-portfolio | `.env.docker` | Build context path | Docker build | Standard |
| `TRADE_MANAGEMENT_CONTEXT` | ${AM_REPO_PATH}\am-trade-management | `.env.docker` | Build context path | Docker build | Standard |
| `MARKET_DATA_CONTEXT` | ${AM_REPO_PATH}\am-market-data | `.env.docker` | Build context path | Docker build | Standard |

---

## 18. GitHub Packages Configuration

| Variable | Value | Location | Purpose | Used By | Type |
|----------|-------|----------|---------|---------|------|
| `GITHUB_PACKAGES_USERNAME` | XXXXXXX | `.env.docker` | GitHub username | Docker build | **SENSITIVE** |
| `GITHUB_PACKAGES_TOKEN` | XXXXXXXXXXXXXXXX | `.env.docker` | GitHub token | Docker build | **SENSITIVE** |

---

## File Structure & Usage

```
am/
├── .env.docker                      ← Main environment file (loaded by docker-compose)
│   Contains: Secrets, DB, Redis, Logging, Policies, OAuth, etc.
│
├── config/services.env              ← Service URLs & protocols
│   Contains: SERVICE_PROTOCOL, Service hosts/ports, URL construction
│
├── docker-compose.yml               ← Service orchestration
│   References: ${VAR_NAME} from .env.docker
│
├── am-api-gateway/
│   └── Reads: AUTH_SERVICE_URL, USER_MANAGEMENT_URL, etc.
│
├── am-auth-tokens/
│   └── Reads: JWT_SECRET, DATABASE_URL, GOOGLE_CLIENT_ID
│
├── am-user-management/
│   └── Reads: AUTH_SERVICE_URL, password policies, email settings
│
└── am-tests/
    ├── DIAGNOSTICS_GUIDE.md         ← API endpoint testing guide
    └── utils/service_diagnostics.py ← Python diagnostic tool
```

---

## Quick Reference: Changing Values

### Change Protocol (HTTP → HTTPS)
```bash
# Edit: config/services.env
SERVICE_PROTOCOL=https
USE_HTTPS=true

# Restart services
docker-compose up -d
```

### Change Database
```bash
# Edit: .env.docker
DATABASE_URL=postgresql://new-user:new-pass@new-host:5432/new-db

# Restart services
docker-compose up -d
```

### Change JWT Secret
```bash
# Edit: .env.docker
JWT_SECRET=your-new-secret-32-chars-minimum-xxxxx
INTERNAL_JWT_SECRET=your-new-internal-secret-xxxxx

# Rebuild services
docker-compose up -d --build
```

### Change Build Context
```bash
# Edit: .env.docker
AM_REPO_PATH=/path/to/new/location

# Rebuild services
docker-compose up -d --build
```

---

## Variable Categories

### 🔴 CRITICAL (Don't Change Without Testing)
- `JWT_SECRET`, `INTERNAL_JWT_SECRET` - Token signing
- `DATABASE_URL` - Data persistence
- `AM_REPO_PATH` - Build context
- `MONGODB_URL`, `KAFKA_BOOTSTRAP_SERVERS` - External services

### 🟡 SENSITIVE (Keep Secure)
- `DB_PASSWORD`, `POSTGRES_PASSWORD` - Database credentials
- `REDIS_PASSWORD` - Cache credentials
- `GOOGLE_CLIENT_SECRET` - OAuth secret
- `SMTP_PASSWORD` - Email credentials
- `GITHUB_PACKAGES_TOKEN` - Package registry

### 🟢 STANDARD (Safe to Modify)
- Service protocols, logging, CORS, rate limiting
- User policies, email settings, subscription terms
- Timeouts, pool sizes, retry settings

---

## Tracking Changes

Use this matrix to track variable changes:

| Date | Variable | Old Value | New Value | Reason | Tested |
|------|----------|-----------|-----------|--------|--------|
| 2025-12-06 | SERVICE_PROTOCOL | http | https | Production deployment | [ ] |
| | | | | | |

