# Environment Configuration Reference

## Overview

The AM Portfolio authentication system uses a **modular environment configuration system** organized across multiple files for better maintainability and scalability.

## Configuration Architecture

### File Organization

```
am/
├── .env.docker                      # Local development overrides (43 lines)
├── config/
│   ├── app.env                      # Core Spring Boot application settings
│   ├── services.env                 # Service URLs and service integration config
│   ├── database.env                 # PostgreSQL, MongoDB, Redis connection strings
│   ├── security.env                 # JWT secrets, OAuth credentials
│   ├── logging.env                  # Logging configuration and levels
│   ├── build.env                    # Build context and Docker settings
│   ├── features.env                 # Feature flags and experimental settings
│   ├── document-processor.env       # Document processor specific config (MongoDB, Kafka, processor settings)
│   ├── portfolio.env                # Portfolio service config (MongoDB, Kafka, Redis, portfolio settings)
│   ├── trade.env                    # Trade service config (MongoDB, Kafka, Redis, trading settings)
│   └── market-data.env              # Market data service config (PostgreSQL, InfluxDB, Kafka, Upstox API)
├── docker-compose.yml               # Core microservices (API Gateway, Auth Tokens, User Management)
├── docker-compose-business.yml      # Business services (Document Processor, Portfolio, Trade API, Market Data)
└── docker-compose-trade.yml         # Standalone trade service for isolated testing
```

## Configuration Files

### 1. `.env.docker` (Local Development Overrides)
**Purpose:** Store sensitive local development overrides and local-only settings  
**Size:** 43 lines (consolidated)  
**Typical Usage:** GitHub tokens, local debugging flags, build context paths

**Key Variables:**
- `GITHUB_TOKEN` - GitHub PAT for private repo access
- `DEBUG_MODE` - Enable debug logging
- `AM_REPO_PATH` - Local repository path for builds

### 2. `config/app.env` (Core Application Settings)
**Purpose:** Spring Boot framework configuration  
**Variables:** Spring profiles, application name, timezone, encoding

### 3. `config/services.env` (Service URLs and Integration)
**Purpose:** Service-to-service communication URLs and integration settings  
**Variables:**
- `PYTHON_SERVICE_URL` - Python internal service URL
- `JAVA_SERVICE_URL` - Java internal service URL
- Service timeout settings

### 4. `config/database.env` (Data Storage Configuration)
**Purpose:** Database connection strings and credentials  
**Variables:**
- `DATABASE_URL` - Primary PostgreSQL connection
- `MONGODB_URL` - MongoDB connection string
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` - Redis connection

### 5. `config/security.env` (Authentication & Authorization)
**Purpose:** JWT secrets and OAuth credentials  
**Variables:**
- `JWT_SECRET` - User token signing secret (32+ chars)
- `INTERNAL_JWT_SECRET` - Service token signing secret (32+ chars)
- `OAUTH_*` - OAuth provider credentials

### 6. `config/logging.env` (Logging Configuration)
**Purpose:** Logging levels and output configuration  
**Variables:**
- `LOG_FORMAT` - `json` (production) or `structured` (dev)
- `LOG_LEVEL` - Root logging level
- `AUDIT_LOG_ENABLED` - Enable audit logging

### 7. `config/build.env` (Docker Build Configuration)
**Purpose:** Docker build-specific settings  
**Variables:**
- `DOCKER_REGISTRY` - Docker registry URL
- `IMAGE_TAG` - Docker image tag

### 8. `config/features.env` (Feature Flags)
**Purpose:** Enable/disable experimental features  
**Variables:**
- `FEATURE_FLAG_*` - Feature toggle variables
- `BETA_FEATURES_ENABLED` - Enable beta features

### 9. `config/document-processor.env` (Document Processor Service)
**Purpose:** Document processor specific configuration  
**Key Variables:**
- `MONGODB_URL` - MongoDB connection for document storage
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker for document events
- `AM_DOCUMENT_PROCESSOR_MAX_RETRIES` - Document processing retry attempts
- `KAFKA_SECURITY_PROTOCOL`, `KAFKA_SASL_MECHANISM` - Kafka security

### 10. `config/portfolio.env` (Portfolio Service)
**Purpose:** Portfolio management service configuration  
**Key Variables:**
- `PORTFOLIO_MONGODB_URL` - MongoDB for portfolio data
- `PORTFOLIO_KAFKA_BOOTSTRAP_SERVERS` - Kafka for portfolio events
- `PORTFOLIO_CREATION_TOPIC`, `PORTFOLIO_UPDATE_TOPIC`, `PORTFOLIO_DELETION_TOPIC`, `PORTFOLIO_REBALANCE_TOPIC`
- `PORTFOLIO_REDIS_HOST`, `PORTFOLIO_REDIS_PORT` - Redis for caching
- `PORTFOLIO_MAX_HOLDINGS` - Maximum holdings per portfolio
- `PORTFOLIO_MIN_INVESTMENT` - Minimum investment amount
- `PORTFOLIO_REBALANCE_THRESHOLD_PERCENT` - Rebalance trigger threshold
- `PORTFOLIO_CACHE_TTL_MINUTES` - Cache expiration
- `PORTFOLIO_THREAD_POOL_SIZE` - Async processing thread pool size

### 11. `config/trade.env` (Trade Service)
**Purpose:** Trade execution service configuration  
**Key Variables:**
- `MONGODB_URI`, `MONGODB_DATABASE` - MongoDB for trade data
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka for trade events
- **Kafka Topics:**
  - `TRADE_CREATION_TOPIC` - New trade creation events
  - `TRADE_EXECUTION_TOPIC` - Trade execution events
  - `TRADE_SETTLEMENT_TOPIC` - Trade settlement events
  - `TRADE_CANCELLATION_TOPIC` - Trade cancellation events
- **Trade Limits:**
  - `TRADE_MIN_QUANTITY` - Minimum trade quantity
  - `TRADE_MAX_QUANTITY` - Maximum trade quantity
  - `TRADE_MIN_PRICE` - Minimum price
  - `TRADE_MAX_PRICE` - Maximum price
  - `TRADE_EXECUTION_TIMEOUT_SECONDS` - Execution timeout
- **Redis Configuration:**
  - `TRADE_REDIS_HOST`, `TRADE_REDIS_PORT`, `TRADE_REDIS_PASSWORD`, `TRADE_REDIS_DB`
- **Thread Pool:**
  - `TRADE_THREAD_POOL_SIZE` - Number of worker threads
  - `TRADE_THREAD_POOL_QUEUE_CAPACITY` - Task queue capacity
- **Retry Configuration:**
  - `TRADE_RETRY_MAX_ATTEMPTS` - Maximum retry attempts
  - `TRADE_RETRY_DELAY_MS` - Delay between retries in milliseconds
- **Order Management:**
  - `TRADE_ORDER_MAX_PENDING` - Maximum pending orders
  - `TRADE_ORDER_VALIDATION_ENABLED` - Order validation flag
  - `TRADE_ORDER_AUDIT_ENABLED` - Order audit logging
- **Risk Management:**
  - `TRADE_RISK_CHECK_ENABLED` - Enable risk checks
  - `TRADE_MAX_DAILY_LOSS_PERCENT` - Daily loss limit
  - `TRADE_MAX_POSITION_SIZE_PERCENT` - Position size limit
- **Market Hours:**
  - `TRADE_MARKET_OPEN_TIME` - Market open time (HH:MM)
  - `TRADE_MARKET_CLOSE_TIME` - Market close time (HH:MM)
  - `TRADE_ENFORCE_MARKET_HOURS` - Enforce market hours flag
- **Settlement:**
  - `TRADE_SETTLEMENT_TYPE` - Settlement type (T+0, T+1, T+2, etc.)
  - `TRADE_AUTO_SETTLEMENT_ENABLED` - Auto-settlement flag
- **Service Integration:**
  - `TRADE_MARKET_DATA_SERVICE_URL` - Market data service endpoint
  - `TRADE_PORTFOLIO_SERVICE_URL` - Portfolio service endpoint
- **Logging & Compliance:**
  - `TRADE_LOG_LEVEL` - Logging level
  - `TRADE_AUDIT_LOG_ENABLED` - Audit logging
  - `TRADE_AUDIT_LOG_RETENTION_DAYS` - Audit log retention
  - `TRADE_COMPLIANCE_CHECK_ENABLED` - Compliance checking

### 12. `config/market-data.env` (Market Data Service)
**Purpose:** Market data service configuration  
**Key Variables:**
- **PostgreSQL:** `MARKET_DATA_POSTGRES_URL`, `MARKET_DATA_POSTGRES_DATABASE`, username, password
- **InfluxDB:** `INFLUXDB_URL`, `INFLUXDB_TOKEN`, `INFLUXDB_ORG`, `INFLUXDB_BUCKET`
- **Kafka Topics:**
  - `STOKUPATE_TOPIC_NAME` - Stock price update topic
  - `NSE_INDICES_TOPIC_NAME` - NSE indices topic
  - `NSE_ETF_TOPIC_NAME` - NSE ETF topic
- **Kafka Configuration:**
  - `MARKET_DATA_KAFKA_BOOTSTRAP_SERVERS` - Kafka broker
  - `KAFKA_CONSUMER_AUTO_OFFSET_RESET` - Consumer offset reset policy
- **Upstox API:**
  - `UPSTOX_CODE` - Upstox API code
  - `UPSTOX_API_KEY` - API key
  - `UPSTOX_SECRET_KEY` - API secret
  - `UPSTOX_ACCESS_TOKEN` - Access token
- **Service Configuration:**
  - `MARKET_DATA_MAX_RETRIES` - Maximum retry attempts
  - `MARKET_DATA_RETRY_DELAY_MS` - Retry delay in milliseconds
  - `MARKET_DATA_THREAD_POOL_SIZE` - Thread pool size
  - `MARKET_DATA_THREAD_QUEUE_CAPACITY` - Queue capacity
  - `MARKET_DATA_MAX_AGE_MINUTES` - Maximum data age in minutes

## Docker Compose Files

### `docker-compose.yml` (Core Services)
**Services:**
- `am-api-gateway` (Port 8000) - API Gateway for client routing
- `am-auth-tokens` (Port 8001) - Token service
- `am-user-management` (Port 8010) - User management service
- `am-python-internal-service` (Port 8002) - Internal Python service (no external port)
- `am-java-internal-service` (Port 8003) - Internal Java service (no external port)

**Usage:**
```bash
# Start core services
docker-compose up -d

# View logs
docker-compose logs -f am-api-gateway

# Stop services
docker-compose down
```

### `docker-compose-business.yml` (Business Services)
**Services:**
- `am-document-processor` (Port 8070) - Document processing service
- `am-portfolio` (Port 8080) - Portfolio management service
- `am-trade-api` (Port 8073) - Trade execution service
- `am-market-data` (Port 8092) - Market data service

**Usage:**
```bash
# Start business services (along with core services)
docker-compose -f docker-compose.yml -f docker-compose-business.yml up -d

# Or just business services
docker-compose -f docker-compose-business.yml up -d

# View logs
docker-compose -f docker-compose-business.yml logs -f am-portfolio

# Stop services
docker-compose -f docker-compose-business.yml down
```

### `docker-compose-trade.yml` (Standalone Trade Service)
**Purpose:** Isolated trade service testing without other services  
**Usage:**
```bash
# Start standalone trade service
docker-compose -f docker-compose-trade.yml up -d

# Test trade service
curl http://localhost:8073/api/v1/trades/health
```

## Loading Environment Variables

### Priority Order
Docker-compose loads environment variables in this order (later overrides earlier):

1. System environment variables
2. `.env` file (if exists in working directory)
3. Files listed in `env_file:` array (in order)
4. `environment:` section in compose file

### Environment Variable Loading

When `docker-compose up` is executed from the `am/` directory:

```yaml
env_file:
  - ./.env.docker                    # 1. Local development overrides
  - ./config/app.env                 # 2. Core app settings
  - ./config/services.env            # 3. Service URLs
  - ./config/database.env            # 4. Database connections
  - ./config/security.env            # 5. JWT secrets
  - ./config/logging.env             # 6. Logging config
  - ./config/build.env               # 7. Build settings
  - ./config/features.env            # 8. Feature flags
  - ./config/document-processor.env  # 9. Service-specific config
```

**Variables are loaded and available to containers via:**
```bash
# Docker will substitute ${VARIABLE_NAME} with values from env files
docker-compose up
```

## Common Configuration Scenarios

### Scenario 1: Development with Debug Logging
```bash
# In .env.docker, set:
DEBUG_MODE=true
LOG_LEVEL=DEBUG

docker-compose up -d
```

### Scenario 2: Running Business Services Only
```bash
cd am/
docker-compose -f docker-compose-business.yml up -d

# Services will load all config files and run independently
# No need for core services (API Gateway, Auth, etc.)
```

### Scenario 3: Custom Environment
```bash
# Create custom env file: config/custom.env
# Add to docker-compose.yml env_file array:
env_file:
  - ./config/custom.env

# Start services
docker-compose up -d
```

### Scenario 4: Production Deployment
```bash
# Set sensitive vars as system environment variables:
export INTERNAL_JWT_SECRET="your-32-char-secret"
export GITHUB_TOKEN="your-github-token"

# Run with minimal override:
docker-compose up -d
# All other vars loaded from modular config files
```

## Modifying Configuration

### Adding a New Environment Variable

1. **Identify which category** the variable belongs to (app, database, security, etc.)
2. **Add to appropriate file** in `config/`:
   ```bash
   # Example: Adding to config/security.env
   NEW_SECURITY_SETTING=value
   ```
3. **Reference in docker-compose.yml**:
   ```yaml
   environment:
     - MY_SETTING=${NEW_SECURITY_SETTING}
   ```
4. **Verify loading**:
   ```bash
   docker-compose config | grep MY_SETTING
   ```

### Changing Service Configuration

1. **Locate the relevant env file** (e.g., `portfolio.env` for portfolio service)
2. **Update the variable value**:
   ```bash
   # Example: Increase portfolio thread pool
   PORTFOLIO_THREAD_POOL_SIZE=30
   ```
3. **Restart the service**:
   ```bash
   docker-compose down am-portfolio
   docker-compose up -d am-portfolio
   ```

## Validation

### Validate Configuration Syntax
```bash
cd am/

# Check core services config
docker-compose config > /dev/null && echo "✅ Valid"

# Check business services config
docker-compose -f docker-compose-business.yml config > /dev/null && echo "✅ Valid"
```

### View Rendered Configuration
```bash
# See how variables are substituted
docker-compose config | less

# Grep specific service
docker-compose config | grep -A 50 "service \"am-portfolio\""
```

### Check Loaded Environment Variables
```bash
# Inside container, verify vars are loaded
docker exec am-portfolio env | grep PORTFOLIO
```

## Troubleshooting

### Variables Show as Undefined (Warnings)
**Issue:** `docker-compose config` shows warnings like "variable is not set"  
**Cause:** Variables from env files don't appear in shell environment during config parsing  
**Solution:** Normal behavior - env files are loaded at runtime, not during config validation

### Service Won't Start (Environment Variables Missing)
**Issue:** Container exits with missing variable error  
**Cause:** Variable not defined in any env file or environment  
**Solution:**
```bash
# 1. Check if variable exists in appropriate env file
grep VARIABLE_NAME config/*.env

# 2. If not found, add it to appropriate file
echo "VARIABLE_NAME=value" >> config/appropriate.env

# 3. Restart service
docker-compose restart service-name
```

### Different Values Between Local and Docker
**Issue:** Environment variable has different value in container vs local  
**Cause:** Loading order - later files override earlier ones  
**Solution:** Check priority order in "Loading Environment Variables" section

## Best Practices

1. **Never put secrets in docker-compose.yml** - Use env files or system environment
2. **Keep related variables together** - Organize by service or category in env files
3. **Use consistent naming** - Follow `SERVICE_SETTING` or `SETTING_TYPE` pattern
4. **Document new variables** - Add comments in env files explaining purpose
5. **Validate after changes** - Always run `docker-compose config` after editing
6. **Use meaningful names** - `TRADE_MAX_QUANTITY` is better than `MAX_QTY`
7. **Set defaults for optional settings** - Make config resilient to missing values

## Related Documentation

- See `ARCHITECTURE.md` for system design
- See `QUICK_START.md` for setup instructions
- See `.env.docker` for local development overrides
- See `config/*.env` files for detailed variable documentation
