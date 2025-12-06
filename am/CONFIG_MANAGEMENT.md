# Environment Configuration Guide

## 📋 Overview

The AM Portfolio authentication system uses a **modular environment configuration** system to manage 150+ variables across multiple services and deployment scenarios.

Instead of a single 236-line `.env.docker` file, variables are now organized into 7 focused configuration files, each with a single clear purpose.

## 📁 Configuration File Structure

```
am/
├── .env.docker                 # Master override file (loaded last)
├── docker-compose.yml          # Service orchestration (uses env_file array)
├── config/                     # Modular configuration directory
│   ├── app.env                 # Core application settings (30 lines)
│   ├── services.env            # Service URLs & networking (40 lines)
│   ├── database.env            # Database connections (50 lines)
│   ├── security.env            # Secrets & credentials (35 lines)
│   ├── logging.env             # Logging configuration (30 lines)
│   ├── build.env               # Build & deployment settings (30 lines)
│   ├── features.env            # Feature flags & toggles (40 lines)
│   └── CONFIG_STRUCTURE.md     # This structure documentation
```

## 🔧 Quick Reference: Where to Edit?

| Need to change... | Edit this file | Lines |
|---|---|---|
| Service hostnames or ports | `config/services.env` | 40 |
| JWT secrets or API keys | `config/security.env` | 35 |
| Database connections | `config/database.env` | 50 |
| App name, version, CORS | `config/app.env` | 30 |
| Log levels or monitoring | `config/logging.env` | 30 |
| Docker image tags | `config/build.env` | 30 |
| Enable/disable features | `config/features.env` | 40 |
| Environment-specific overrides | `.env.docker` | variable |

## 📄 Configuration Files in Detail

### 1. **config/app.env** - Core Application Settings
**30 lines** | Core application behavior and metadata

```bash
ENVIRONMENT=development
DEBUG=false
APP_TITLE=AM Portfolio Authentication System
APP_VERSION=1.0.0

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Email Service
EMAIL_SERVICE=mock
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Build Context
AM_REPO_PATH=.
```

**Use this file when:**
- Changing application name or version
- Enabling/disabling debug mode
- Updating CORS allowed origins
- Configuring email service settings

### 2. **config/services.env** - Service URLs & Networking
**40 lines** | Internal and external service endpoints

```bash
# Service Protocol (http, https, grpc)
SERVICE_PROTOCOL=http

# Service Hostnames & Ports
SERVICE_HOST_API_GATEWAY=am-api-gateway
SERVICE_PORT_API_GATEWAY=8000

SERVICE_HOST_AUTH_TOKENS=auth-tokens
SERVICE_PORT_AUTH_TOKENS=8001

SERVICE_HOST_USER_MGMT=am-user-management
SERVICE_PORT_USER_MGMT=8010

# Computed Service URLs (used in application)
AUTH_SERVICE_URL=${SERVICE_PROTOCOL}://auth-tokens:8001
USER_MANAGEMENT_URL=${SERVICE_PROTOCOL}://am-user-management:8010
PYTHON_SERVICE_URL=${SERVICE_PROTOCOL}://am-python-internal-service:8002
```

**Use this file when:**
- Adding new microservices
- Changing service hostnames or ports
- Switching between HTTP/HTTPS
- Configuring service discovery

### 3. **config/database.env** - Database Connections
**50 lines** | All database connection strings and credentials

```bash
# PostgreSQL
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=am_portfolio
DATABASE_USER=am_user
DATABASE_PASSWORD=secure_password_here
DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}

# PostgreSQL Connection Pool
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30

# MongoDB
MONGODB_URL=mongodb://mongo:27017/am_portfolio

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
```

**Use this file when:**
- Changing database host, port, or credentials
- Adding new databases
- Adjusting connection pool sizes
- Configuring database backup or replication

### 4. **config/security.env** - Secrets & Credentials
**35 lines** | JWT secrets, OAuth credentials, external API keys

```bash
# JWT Configuration
JWT_SECRET=your-secure-32-character-jwt-secret-here
INTERNAL_JWT_SECRET=your-secure-32-character-internal-jwt-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OAuth - Google
GOOGLE_OAUTH_ENABLED=false
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - GitHub
GITHUB_OAUTH_ENABLED=false
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# External Service Credentials
GITHUB_PACKAGES_TOKEN=your-github-token
GITHUB_PACKAGES_USER=your-github-username
```

**🔐 CRITICAL SECURITY NOTES:**
- **Never commit `security.env` to git** - Add to `.gitignore`
- Use a secrets manager (AWS Secrets Manager, HashiCorp Vault) in production
- Keep JWT secrets 32+ characters, random, and unique per environment
- Rotate secrets regularly
- Use environment-specific credentials

### 5. **config/logging.env** - Logging & Monitoring
**30 lines** | Logging levels, formats, and monitoring configuration

```bash
# Global Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_CONSOLE=true
LOG_FILE_PATH=/var/log/app
LOG_MAX_FILE_SIZE=10485760

# Service-Specific Log Levels
USER_MGMT_LOG_LEVEL=INFO
AUTH_TOKENS_LOG_LEVEL=INFO
INTERNAL_SERVICE_LOG_LEVEL=INFO

# Monitoring & Debug
ENABLE_DEBUG_LOGGING=false
ENABLE_METRICS=true
ENABLE_HEALTH_CHECKS=true
```

**Use this file when:**
- Troubleshooting application issues
- Enabling detailed logging for specific services
- Configuring log format for production vs development
- Adjusting monitoring and metrics collection

### 6. **config/build.env** - Build & Deployment
**30 lines** | Docker build settings, image tagging, resource limits

```bash
# Repository & Build Context
AM_REPO_PATH=.

# Docker Configuration
DOCKER_BUILD_CONTEXT=.
DOCKER_BUILDKIT=1
DOCKER_BUILD_PROGRESS=auto

# Docker Compose
COMPOSE_PROJECT_NAME=am-portfolio
COMPOSE_IGNORE_ORPHANS=true

# Image Tagging
DOCKER_REGISTRY=
IMAGE_TAG=latest
IMAGE_VERSION=1.0.0

# Deployment
DEPLOYMENT_ENV=development
ENVIRONMENT=development

# Resource Limits
CPU_LIMIT=2
MEMORY_LIMIT=2g
```

**Use this file when:**
- Setting up CI/CD pipelines
- Configuring resource limits
- Managing Docker image versions
- Deploying to different environments

### 7. **config/features.env** - Feature Flags
**40 lines** | Toggle experimental features and integrations

```bash
# Authentication Features
ENABLE_OAUTH_GOOGLE=false
ENABLE_OAUTH_GITHUB=false
ENABLE_MFA=false
ENABLE_PASSWORDLESS_AUTH=false

# API Features
ENABLE_API_RATE_LIMITING=true
ENABLE_API_CACHING=true
ENABLE_SWAGGER_UI=true

# Monitoring & Observability
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_REQUEST_TRACING=true
ENABLE_ERROR_TRACKING=true

# External Services
ENABLE_DOCUMENT_PROCESSOR=false
ENABLE_PORTFOLIO_SERVICE=false
ENABLE_TRADE_API=false

# Beta & Experimental
ENABLE_BETA_FEATURES=false
ENABLE_EXPERIMENTAL_API=false
```

**Use this file when:**
- Testing new features in development/staging
- Enabling OAuth integrations
- Gradually rolling out features to production
- A/B testing new functionality

## 🚀 How Configuration Loading Works

### Docker Compose Loading Order

When you run `docker-compose up`, services load environment variables in this order:

```yaml
env_file:
  - .env.docker                    # 1. Master overrides (load first)
  - ./config/app.env              # 2. Core app settings
  - ./config/services.env         # 3. Service URLs
  - ./config/database.env         # 4. Database config
  - ./config/security.env         # 5. Secrets
  - ./config/logging.env          # 6. Logging config
  - ./config/build.env            # 7. Build settings
  - ./config/features.env         # 8. Feature flags (load last)
```

**Variable Override Precedence** (highest to lowest):
1. `environment:` section in docker-compose.yml (highest priority)
2. `.env.docker` file
3. `config/features.env`
4. `config/build.env`
5. `config/logging.env`
6. `config/security.env`
7. `config/database.env`
8. `config/services.env`
9. `config/app.env` (lowest priority)

**Example:** If `LOG_LEVEL=INFO` is set in multiple files, the value from `.env.docker` will be used.

## 🔄 Variable Substitution

Variables can reference other variables using `${VARIABLE_NAME}` syntax:

**config/database.env:**
```bash
DATABASE_USER=am_user
DATABASE_PASSWORD=secure_pass
DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@localhost:5432/am_portfolio
```

**config/services.env:**
```bash
SERVICE_PROTOCOL=http
SERVICE_HOST_AUTH=auth-tokens
SERVICE_PORT_AUTH=8001
AUTH_SERVICE_URL=${SERVICE_PROTOCOL}://${SERVICE_HOST_AUTH}:${SERVICE_PORT_AUTH}
```

## 🛠️ Common Tasks

### Task 1: Switch All Services from HTTP to HTTPS

**Before:** All services use `http://`
```bash
# config/services.env
SERVICE_PROTOCOL=http
AUTH_SERVICE_URL=http://auth-tokens:8001
USER_MANAGEMENT_URL=http://am-user-management:8010
```

**After:** Change one line
```bash
# config/services.env
SERVICE_PROTOCOL=https
# URLs automatically become: https://auth-tokens:8001, https://am-user-management:8010
```

### Task 2: Increase Database Connection Pool for Production

```bash
# config/database.env
DATABASE_POOL_SIZE=50        # Changed from 20
DATABASE_MAX_OVERFLOW=20     # Changed from 10
DATABASE_POOL_TIMEOUT=60     # Changed from 30
```

### Task 3: Enable OAuth for Staging

```bash
# config/features.env
ENABLE_OAUTH_GOOGLE=true
```

```bash
# config/security.env
GOOGLE_CLIENT_ID=staging-client-id
GOOGLE_CLIENT_SECRET=staging-client-secret
```

### Task 4: Deploy to Different Environment

1. Create environment-specific override file:
   ```bash
   cp .env.docker .env.production
   ```

2. Edit production-specific values:
   ```bash
   # .env.production
   ENVIRONMENT=production
   DEBUG=false
   LOG_FORMAT=json
   JWT_EXPIRATION_HOURS=1
   DATABASE_HOST=prod-db.company.com
   ```

3. Load environment-specific file:
   ```bash
   export $(cat .env.production | xargs)
   docker-compose up -d
   ```

## ✅ Configuration Validation

### Verify All Variables Are Set

```bash
# Check for undefined variables in docker-compose.yml
docker-compose config

# This command will show any errors if variables are missing
```

### Validate Configuration Files

```bash
# Check for syntax errors in env files
for file in .env.docker config/*.env; do
    echo "Checking $file..."
    grep -E '^[^#]*\$\{[A-Z_]+\}' "$file" | grep -v '${' || echo "  ✓ No undefined variables"
done
```

### Test Service Startup

```bash
# Start services with new configuration
docker-compose up --no-start

# Check health
docker-compose ps

# View logs if issues occur
docker-compose logs -f
```

## 📊 Environment-Specific Configurations

For different deployment environments, create environment-specific files:

```
config/
├── app.env                    # Shared base
├── services.env               # Shared base
├── database.env               # Shared base
├── security.env               # Shared base
├── logging.env                # Shared base
├── build.env                  # Shared base
├── features.env               # Shared base
└── environments/
    ├── development.env        # Dev overrides
    ├── staging.env            # Staging overrides
    ├── production.env         # Prod overrides
    └── testing.env            # Test overrides
```

**Loading environment-specific config:**
```bash
# In docker-compose.yml or deployment script
env_file:
  - config/app.env
  - config/services.env
  - config/database.env
  - config/security.env
  - config/logging.env
  - config/build.env
  - config/features.env
  - config/environments/production.env  # Environment-specific overrides
  - .env.docker                          # Final local overrides
```

## 🔐 Security Best Practices

### 1. **Never Commit Secrets**
```bash
# .gitignore
config/security.env
.env.docker
.env.*.local
config/environments/*/security.env
```

### 2. **Use Secrets Manager in Production**

Instead of storing secrets in .env files:
- **AWS**: Use AWS Secrets Manager or Parameter Store
- **Azure**: Use Azure Key Vault
- **Kubernetes**: Use Kubernetes Secrets
- **HashiCorp**: Use Vault

### 3. **Rotate Secrets Regularly**

```bash
# Example: Rotate JWT secret
1. Generate new JWT_SECRET
2. Update config/security.env
3. Redeploy services
4. Monitor for errors
5. Remove old secret after grace period
```

### 4. **Separate Credentials by Environment**

```bash
# config/environments/production.env
DATABASE_HOST=prod-db.company.com
DATABASE_USER=prod_user
JWT_SECRET=${PRODUCTION_JWT_SECRET}  # From secrets manager

# config/environments/development.env
DATABASE_HOST=localhost
DATABASE_USER=dev_user
JWT_SECRET=dev-key-not-for-production
```

## 📝 .env.docker Reference

The `.env.docker` file contains **environment-specific overrides** and is the last file loaded, giving it highest priority.

Typical use cases:
- Local development overrides
- CI/CD environment variables
- Docker Compose specific settings
- Deployment-time configuration

**Example `.env.docker` (Don't commit to git):**
```bash
# Local Development Overrides
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=structured

# Local Database Override
DATABASE_HOST=host.docker.internal
DATABASE_URL=postgresql://dev_user:dev_pass@host.docker.internal:5432/am_portfolio

# Local Service Overrides
AUTH_SERVICE_URL=http://localhost:8001
USER_MANAGEMENT_URL=http://localhost:8010
```

## 🎯 Summary of Changes

| Aspect | Before | After |
|---|---|---|
| **Total Files** | 1 file (.env.docker) | 8 files (1 + 7 config files) |
| **Lines per File** | 236 lines | 30-50 lines per config file |
| **Organization** | Monolithic | Modular by function |
| **Maintenance** | Hard to find variables | Easy to locate by purpose |
| **Env-specific Config** | Manual duplication | Separate config files |
| **Variable Tracking** | Difficult | Clear mapping in docs |

## 🚀 Getting Started

### First-Time Setup

```bash
# 1. Navigate to project directory
cd am

# 2. Copy template files (already created)
# - config/app.env
# - config/services.env
# - config/database.env
# - config/security.env
# - config/logging.env
# - config/build.env
# - config/features.env

# 3. Create local override file
cp .env.docker.example .env.docker

# 4. Edit .env.docker with your local values
# (especially security.env variables - use secrets manager in production)

# 5. Verify configuration
docker-compose config

# 6. Start services
docker-compose up -d

# 7. Check health
curl http://localhost:8000/health
```

### Running with Different Environments

```bash
# Development
docker-compose -f docker-compose.yml up -d

# Staging (with overrides)
export $(cat config/environments/staging.env | xargs)
docker-compose up -d

# Production (with secrets manager)
export ENVIRONMENT=production
export DATABASE_HOST=$(aws secretsmanager get-secret-value --secret-id am-portfolio/db-host --query SecretString --output text)
docker-compose up -d
```

## 📚 Related Documentation

- **[VARIABLES_INVENTORY.md](./VARIABLES_INVENTORY.md)** - Complete list of all 150+ variables with descriptions
- **[SERVICE_URL_CONFIG.md](./SERVICE_URL_CONFIG.md)** - Detailed service URL configuration
- **[DIAGNOSTICS_GUIDE.md](./am-tests/DIAGNOSTICS_GUIDE.md)** - System health check endpoints
- **[Architecture](../docs/ARCHITECTURE.md)** - Overall system design
- **[Security](../docs/SECURITY.md)** - Security patterns and compliance

## ❓ FAQ

**Q: What's the difference between `.env.docker` and `config/*.env`?**
A: `.env.docker` contains local/environment-specific overrides, while `config/*.env` files are shared templates that apply to all environments.

**Q: Should I commit `config/*.env` files?**
A: Yes! They're templates. Only exclude `config/security.env` from git (or remove credentials from the committed version).

**Q: How do I use this with Kubernetes?**
A: Instead of env_file, use ConfigMaps for non-sensitive data and Secrets for sensitive data.

**Q: Can I use this with environment-specific deployments?**
A: Yes! Create `config/environments/*.env` files with overrides per environment.

**Q: What if a variable is not set?**
A: Docker Compose will show an error. Check `docker-compose config` output to see which variables are missing.
