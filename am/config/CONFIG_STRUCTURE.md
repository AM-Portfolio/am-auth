# ═══════════════════════════════════════════════════════════════
# CONFIGURATION STRUCTURE & LOADING ORDER
# ═══════════════════════════════════════════════════════════════
# This document describes how to load and manage modular config files
# ═══════════════════════════════════════════════════════════════

## Config Files Organization

### 1. **services.env** - Service URLs & Networking
   - `SERVICE_PROTOCOL` - HTTP/HTTPS/gRPC protocol
   - `SERVICE_HOST_*` - Service hostnames
   - `SERVICE_PORT_*` - Service ports
   - `*_SERVICE_URL` - Computed service URLs
   - **Use Case**: When adding new microservices or changing service endpoints
   - **Lines**: ~40

### 2. **database.env** - Database Connections
   - PostgreSQL: host, port, credentials, connection pools
   - MongoDB: connection URL and options
   - Redis: connection strings and passwords
   - Kafka: bootstrap servers and security
   - **Use Case**: Database configuration, credentials, performance tuning
   - **Lines**: ~50

### 3. **security.env** - Secrets & Credentials
   - `JWT_SECRET` - User token signing key
   - `INTERNAL_JWT_SECRET` - Service token signing key
   - OAuth: Google, GitHub, other providers
   - External service credentials (API keys, tokens)
   - **Use Case**: Secrets management, credential rotation
   - **Lines**: ~35
   - **🔴 CRITICAL**: Never commit to git, use secrets management in production

### 4. **app.env** - Core Application Settings
   - `ENVIRONMENT` - development/staging/production
   - CORS settings, email configuration
   - Application title, version, description
   - Build context (AM_REPO_PATH)
   - **Use Case**: Global application behavior
   - **Lines**: ~30

### 5. **logging.env** - Logging & Monitoring
   - Global log levels and formats
   - Service-specific log configurations
   - Debug settings
   - **Use Case**: Troubleshooting, performance monitoring
   - **Lines**: ~30

### 6. **build.env** - Build & Deployment
   - Docker build contexts
   - Image tagging and versioning
   - Resource limits
   - Deployment environment
   - **Use Case**: CI/CD pipelines, local development
   - **Lines**: ~30

### 7. **features.env** - Feature Flags
   - OAuth features: Google, GitHub, MFA, passwordless
   - API features: rate limiting, caching, Swagger
   - Monitoring: APM, tracing, error tracking
   - External services: portfolio, documents, trading
   - Beta & experimental features
   - **Use Case**: A/B testing, gradual rollouts, feature management
   - **Lines**: ~40

## Total Config Size
- Individual files: 25-50 lines each (organized and readable)
- Total variables: 150+ (same as before, but organized)
- Main .env.docker: Now a master orchestrator instead of monolithic file

## Loading Strategy

### For Docker Compose
```yaml
# docker-compose.yml uses env_file array to load multiple files
services:
  app:
    env_file:
      - .env.docker        # Master override file
      - config/app.env
      - config/services.env
      - config/database.env
      - config/security.env
      - config/logging.env
      - config/build.env
      - config/features.env
```

### For Python Applications
```python
# Load multiple env files in order
from dotenv import load_dotenv
from pathlib import Path

config_dir = Path(__file__).parent / "config"
env_files = [
    ".env.docker",                    # Master overrides
    config_dir / "app.env",           # Core settings
    config_dir / "services.env",      # Service URLs
    config_dir / "database.env",      # Database config
    config_dir / "security.env",      # Secrets
    config_dir / "logging.env",       # Logging
    config_dir / "build.env",         # Build settings
    config_dir / "features.env"       # Feature flags
]

for env_file in env_files:
    load_dotenv(env_file, override=True)
```

## Benefits of Modular Configuration

✅ **Organized**: Each file has a single clear purpose
✅ **Readable**: No more 236-line monolithic files
✅ **Maintainable**: Easy to find and modify specific variables
✅ **Scalable**: Simple to add new config files as needs grow
✅ **Auditable**: Clear tracking of which file manages what
✅ **Env-specific**: Can swap entire config file sets for dev/staging/prod
✅ **Git-friendly**: Easy to manage .gitignore (only security.env excluded)

## Quick Reference by Use Case

### 🔧 Changing Service Ports?
→ Edit `config/services.env`

### 🔐 Rotating JWT Secrets?
→ Edit `config/security.env` (don't commit, use secrets manager)

### 📊 Enabling Monitoring?
→ Edit `config/logging.env`

### 🎌 Testing New Feature?
→ Edit `config/features.env`

### 🏗️ Adding New Database?
→ Edit `config/database.env`

### 🚀 Deploying to Production?
→ Use production-specific values in all env files

## Environment-Specific Configuration

For different environments, create copies:

```
config/
├── app.env                    # Shared base
├── database.env               # Shared base
├── security.env               # Shared base (overridden by secrets manager)
├── services.env               # Shared base
├── logging.env                # Shared base
├── build.env                  # Shared base
├── features.env               # Shared base
├── environments/
│   ├── development.env        # Dev overrides
│   ├── staging.env            # Staging overrides
│   ├── production.env         # Prod overrides
```

Then load environment-specific file after base files to override values.

## Configuration Validation

Before deploying, verify all variables are set:

```bash
# Check for undefined variables
grep -r '\${[A-Z_]*}' docker-compose.yml

# Test with docker-compose validation
docker-compose config

# Verify all services start with new config
docker-compose up --no-start
```

## Migration from Monolithic to Modular

**Step 1**: Create modular config files ✅ (DONE)
**Step 2**: Update docker-compose.yml to use env_file array (TODO)
**Step 3**: Test docker-compose with new configuration (TODO)
**Step 4**: Update .env.docker to document loading order (TODO)
**Step 5**: Add environment-specific overrides (TODO)
**Step 6**: Update documentation with new structure (TODO)
