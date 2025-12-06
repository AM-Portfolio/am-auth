# Service URL Configuration Guide

## Quick Switch: HTTP vs HTTPS

### Current Setup (HTTP with Ports)
```env
SERVICE_PROTOCOL=http
USE_HTTPS=false
```

All service URLs include ports:
- `http://auth-tokens:8001`
- `http://am-user-management:8000`
- `http://am-python-internal-service:8002`
- etc.

---

### Switch to HTTPS (No Ports)

Simply change `.env.docker`:

```env
SERVICE_PROTOCOL=https
USE_HTTPS=true
```

All service URLs will use HTTPS without ports:
- `https://auth-tokens`
- `https://am-user-management`
- `https://am-python-internal-service`
- etc.

---

## How It Works

The `.env.docker` file defines service URLs using variables:

```env
AUTH_TOKENS_SERVICE_HOST=auth-tokens
AUTH_TOKENS_SERVICE_PORT=8001
AUTH_SERVICE_URL=${SERVICE_PROTOCOL}://${AUTH_TOKENS_SERVICE_HOST}:${AUTH_TOKENS_SERVICE_PORT}
```

When expanded:
- **HTTP Mode**: `http://auth-tokens:8001`
- **HTTPS Mode**: Change `SERVICE_PROTOCOL=https` → `https://auth-tokens:8001`

---

## All Service URL Variables

The following service URLs are controlled by variables in `.env.docker`:

| Service | Variable | HTTP | HTTPS |
|---------|----------|------|-------|
| Auth Tokens | `AUTH_SERVICE_URL` | `http://auth-tokens:8001` | `https://auth-tokens` |
| User Management | `USER_MANAGEMENT_URL` | `http://am-user-management:8000` | `https://am-user-management` |
| Python Internal | `PYTHON_SERVICE_URL` | `http://am-python-internal-service:8002` | `https://am-python-internal-service` |
| Java Internal | `JAVA_SERVICE_URL` | `http://am-java-internal-service:8003` | `https://am-java-internal-service` |
| Document Processor | `DOCUMENT_PROCESSOR_URL` | `http://am-document-processor:8070` | `https://am-document-processor` |
| Portfolio | `PORTFOLIO_URL` | `http://am-portfolio:8080` | `https://am-portfolio` |
| Trade API | `TRADE_API_URL` | `http://am-trade-api:8073` | `https://am-trade-api` |
| Market Data | `MARKET_DATA_URL` | `http://am-market-data:8092` | `https://am-market-data` |

---

## Usage Examples

### Example 1: Development (HTTP)
```env
SERVICE_PROTOCOL=http
USE_HTTPS=false
```
Then: `docker-compose up -d`

### Example 2: Production (HTTPS)
```env
SERVICE_PROTOCOL=https
USE_HTTPS=true
```
Then: `docker-compose up -d`

### Example 3: Custom Protocol
```env
SERVICE_PROTOCOL=grpc
USE_HTTPS=false
```
Then: `docker-compose up -d`

---

## Individual Service Configuration

You can also override individual service hosts if needed:

```env
# Override just the auth service host
AUTH_TOKENS_SERVICE_HOST=custom-auth-host.example.com
AUTH_TOKENS_SERVICE_PORT=443
# Result: https://custom-auth-host.example.com:443 (if HTTPS enabled)
```

---

## Tips

✅ **Best Practice**: Keep all services on the same protocol (HTTP or HTTPS)

✅ **Easy Migration**: Just change `SERVICE_PROTOCOL` and `USE_HTTPS` in one file

✅ **No Restart Needed**: Change `.env.docker`, then `docker-compose up -d` applies new URLs

❌ **Avoid**: Don't manually edit docker-compose.yml service URLs - use .env.docker instead

