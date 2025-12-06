# System Diagnostics & Testing Guide

Complete guide to testing your AM Authentication System using API endpoints (instead of shell scripts). Perfect for Docker deployments!

---

## 📋 Overview

Instead of using shell scripts (which don't work well in Docker), you can now use **API endpoints** to:

✅ Check if all services are up  
✅ Get count of how many APIs are running  
✅ Test database connection stability  
✅ Verify inter-service communication  
✅ Test all Python scripts from a single place  
✅ Get real-time diagnostics and health reports  

---

## 🚀 Quick Start

### 1. Start the System
```bash
cd am
docker-compose up -d --build
```

### 2. Test Using API Endpoints

**Get Complete System Health:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/system/health
```

**Get Service Count:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/system/services/status
```

**Check Database:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/system/database/status
```

---

## 🔍 Available Endpoints

### 1. **Complete System Diagnostics**

**Endpoint:** `GET /api/v1/system/health`

**Purpose:** Get comprehensive health check of entire system

**Response:**
```json
{
  "timestamp": "2025-12-06T10:30:45.123456",
  "overall_status": "healthy",
  "total_services": 5,
  "services_up": 5,
  "services_down": 0,
  "services": [
    {
      "service_name": "API Gateway",
      "port": 8000,
      "status": "online",
      "response_time_ms": 2.34
    },
    {
      "service_name": "User Management",
      "port": 8010,
      "status": "online",
      "response_time_ms": 5.12
    }
    // ... more services
  ],
  "database": {
    "database": "PostgreSQL",
    "connection_status": "connected",
    "response_time_ms": 1.5,
    "table_count": 8
  },
  "python_scripts": [
    {
      "script_name": "Document Processor Tests",
      "location": "am/am-tests/unit/test_document_processor.py",
      "status": "success"
    }
    // ... more scripts
  ]
}
```

**When to use:** Initial system validation, Docker startup verification, comprehensive health check

---

### 2. **Services Status**

**Endpoint:** `GET /api/v1/system/services/status`

**Purpose:** Quick check of all microservices

**Response:**
```json
{
  "timestamp": "2025-12-06T10:30:45.123456",
  "total_services": 5,
  "services_up": 5,
  "services_down": 0,
  "services": [
    {
      "service_name": "API Gateway",
      "port": 8000,
      "status": "online",
      "response_time_ms": 2.34
    },
    // ... all services with status
  ]
}
```

**When to use:** 
- How many APIs are running? → Check `services_up`
- Quick health check
- Monitoring dashboards

---

### 3. **Database Status**

**Endpoint:** `GET /api/v1/system/database/status`

**Purpose:** Check database connection and stability

**Response:**
```json
{
  "timestamp": "2025-12-06T10:30:45.123456",
  "database": {
    "database": "PostgreSQL",
    "connection_status": "connected",
    "response_time_ms": 1.5,
    "table_count": 8
  }
}
```

**When to use:**
- Is database connection stable?
- Database performance check
- Table count verification

---

### 4. **Python Scripts Status**

**Endpoint:** `GET /api/v1/system/python-scripts/status`

**Purpose:** Check availability of all Python test scripts

**Response:**
```json
{
  "timestamp": "2025-12-06T10:30:45.123456",
  "total_scripts": 3,
  "available_scripts": 3,
  "scripts": [
    {
      "script_name": "Document Processor Tests",
      "location": "am/am-tests/unit/test_document_processor.py",
      "status": "success"
    },
    {
      "script_name": "Service Verification",
      "location": "am/am-tests/integration/verify_all_services.py",
      "status": "success"
    },
    {
      "script_name": "Market Data Proxy",
      "location": "am/am-tests/e2e/test_market_data_proxy.py",
      "status": "success"
    }
  ]
}
```

**When to use:**
- Verify all test scripts are in place
- Before running Python tests

---

### 5. **Run Full Diagnostics**

**Endpoint:** `POST /api/v1/system/diagnostics/run`

**Query Parameters:**
- `include_python_tests` (bool, default: true) - Check Python scripts

**Purpose:** Trigger complete system diagnostics

**Response:**
```json
{
  "diagnostics": {
    // ... full SystemDiagnosticsResponse
  },
  "check_completed_in_seconds": 2.456,
  "timestamp": "2025-12-06T10:30:45.123456"
}
```

**When to use:**
- CI/CD pipeline validation
- Docker deployment checks
- Complete system verification

---

### 6. **System Information**

**Endpoint:** `GET /api/v1/system/info`

**Purpose:** Get system info and available diagnostics endpoints

**Response:**
```json
{
  "system": "AM Authentication & Asset Management",
  "version": "1.0.0",
  "environment": "Docker Microservices",
  "timestamp": "2025-12-06T10:30:45.123456",
  "services": {
    "api_gateway": "http://localhost:8000",
    "user_management": "http://user-management:8010",
    "auth_tokens": "http://auth-tokens:8001",
    "python_internal_service": "http://python-internal-service:8002",
    "java_internal_service": "http://java-internal-service:8003"
  },
  "diagnostics_endpoints": {
    "full_health_check": "/api/v1/system/health",
    "services_status": "/api/v1/system/services/status",
    "database_status": "/api/v1/system/database/status",
    "python_scripts": "/api/v1/system/python-scripts/status",
    "run_diagnostics": "/api/v1/system/diagnostics/run",
    "system_info": "/api/v1/system/info"
  },
  "test_scripts_location": "am/am-tests/"
}
```

---

## 🐍 Using Python Tests

### Option 1: Direct Python Script

Run the test service diagnostics directly:

```bash
cd am/am-tests
python -m utils.service_diagnostics
```

**Output:**
```
AM System Diagnostics Client
======================================================================

1️⃣ Getting system info...
   System: AM Authentication & Asset Management v1.0.0

2️⃣ Checking services status...
✅ Services: 5/5 online

3️⃣ Checking database connection...
✅ Database connected (1.5ms)

4️⃣ Checking inter-service communication...
✅ All 5 services online - communication possible

5️⃣ Printing full health report...

======================================================================
SYSTEM DIAGNOSTICS REPORT
======================================================================
Timestamp: 2025-12-06T10:30:45.123456
Overall Status: HEALTHY
Services: 5/5 online
Database: connected

Service Status:
  ✅ API Gateway: online (2.34ms)
  ✅ User Management: online (5.12ms)
  ✅ Auth Tokens: online (3.45ms)
  ✅ Python Internal Service: online (4.23ms)
  ✅ Java Internal Service: online (6.78ms)

======================================================================

✅ Diagnostics complete!
```

---

### Option 2: Use in Your Python Tests

```python
from am_tests.utils.service_diagnostics import (
    ServiceDiagnostics,
    create_diagnostics_client,
    test_all_services,
    test_database_connection
)

# Create client
diagnostics = create_diagnostics_client()

# Test all services
if test_all_services(diagnostics):
    print("All APIs are up!")

# Test database
if test_database_connection(diagnostics):
    print("Database is stable!")

# Get service count
count = diagnostics.get_services_count()
print(f"Services up: {count['up']}/{count['total']}")

# Assert all services are up
diagnostics.assert_all_services_up()

# Get full health report
health = diagnostics.get_system_health()
print(f"Overall status: {health['overall_status']}")
```

---

### Option 3: Using pytest

```bash
cd am/am-tests
pytest integration/test_system_health.py -v
```

**Output:**
```
test_system_health.py::TestSystemDiagnostics::test_api_gateway_responds PASSED ✅
test_system_health.py::TestSystemDiagnostics::test_all_services_status PASSED ✅
test_system_health.py::TestSystemDiagnostics::test_services_are_online PASSED ✅
test_system_health.py::TestSystemDiagnostics::test_database_connection PASSED ✅
test_system_health.py::TestServiceHealth::test_api_gateway_online PASSED ✅
test_system_health.py::TestDatabaseHealth::test_database_connected PASSED ✅

====== 9 passed in 2.34s ======
```

---

## 🎯 Common Use Cases

### Use Case 1: "How many APIs are up?"

**API Call:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/system/services/status
```

**Extract count:**
```bash
curl -s -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/system/services/status | jq '.services_up'
```

**Or using Python:**
```python
diagnostics = create_diagnostics_client()
count = diagnostics.get_services_count()
print(f"APIs up: {count['up']}")  # Output: APIs up: 5
```

---

### Use Case 2: "Is database connection stable?"

**API Call:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/system/database/status
```

**Python:**
```python
diagnostics = create_diagnostics_client()
if test_database_connection(diagnostics):
    print("✅ Database is stable")
else:
    print("❌ Database connection issues")
```

---

### Use Case 3: "Are all services communicating?"

**Python:**
```python
diagnostics = create_diagnostics_client()
if test_inter_service_communication(diagnostics):
    print("✅ All services can communicate")
else:
    print("❌ Some services cannot communicate")
```

---

### Use Case 4: "Can I run Python scripts?"

**API Call:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/system/python-scripts/status
```

**Response shows** if all Python scripts are available and where they are located

---

## 🔒 Authentication

All diagnostics endpoints require a valid JWT token:

```bash
# Set token in headers
Authorization: Bearer YOUR_JWT_TOKEN
```

**Get a test token:**

```bash
# First register a user
curl -X POST http://localhost:8010/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# Activate the user (use user_id from registration)
curl -X POST http://localhost:8010/api/v1/users/{USER_ID}/activate

# Get token (login)
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'

# Use the token in diagnostics requests
curl -H "Authorization: Bearer {TOKEN}" \
  http://localhost:8000/api/v1/system/health
```

---

## 📊 Docker Integration

### Add to Docker Entrypoint

Create a health check script:

```bash
#!/bin/bash
# wait-for-health.sh

echo "Waiting for all services to be healthy..."

for i in {1..30}; do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer TEST_TOKEN" \
    http://localhost:8000/api/v1/system/health)
  
  if [ "$RESPONSE" = "200" ]; then
    echo "✅ System is healthy"
    exit 0
  fi
  
  echo "Attempt $i/30: System still starting... ($RESPONSE)"
  sleep 2
done

echo "❌ System failed to become healthy"
exit 1
```

### Use in docker-compose.yml

```yaml
services:
  am-api-gateway:
    # ... other config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

## 📈 Monitoring & Alerting

### Example: Continuous Monitoring

```python
import time
from datetime import datetime
from service_diagnostics import create_diagnostics_client

diagnostics = create_diagnostics_client()

while True:
    try:
        health = diagnostics.get_system_health()
        
        timestamp = datetime.now().isoformat()
        status = health['overall_status']
        services_up = health['services_up']
        
        print(f"[{timestamp}] Status: {status} | Services: {services_up}/5")
        
        # Alert if any service down
        if health['services_down'] > 0:
            print(f"⚠️ ALERT: {health['services_down']} services down!")
        
        # Alert if database disconnected
        if health['database']['connection_status'] != "connected":
            print("⚠️ ALERT: Database disconnected!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(30)  # Check every 30 seconds
```

---

## 🛠️ Troubleshooting

### Problem: "Unauthorized" Error

**Solution:** Use a valid JWT token in `Authorization: Bearer` header

```bash
# Get token first
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' | jq -r '.access_token')

# Use token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/health
```

---

### Problem: "Service not found" Error

**Solution:** Ensure Docker services are running

```bash
# Check Docker containers
docker-compose ps

# Check logs
docker-compose logs am-api-gateway
```

---

### Problem: Database shows "disconnected"

**Solution:** Check database container

```bash
# View database logs
docker-compose logs postgres

# Verify connection string in .env.docker
cat am/.env.docker | grep DATABASE_URL
```

---

## 📚 File Structure

```
am/
├── am-tests/
│   ├── utils/
│   │   ├── service_diagnostics.py  ← Diagnostics client library
│   │   └── generate_token.py
│   ├── integration/
│   │   ├── test_system_health.py   ← Main test suite
│   │   ├── verify_all_services.py
│   │   └── verify_security_failure.py
│   ├── unit/
│   ├── e2e/
│   └── scripts/
│
├── am-api-gateway/
│   ├── api/v1/endpoints/
│   │   ├── diagnostics.py          ← Diagnostics endpoints
│   │   ├── documents.py
│   │   └── ...
│   └── main.py
```

---

## ✅ Checklist: Docker Deployment

- [ ] All services start in docker-compose.yml
- [ ] API Gateway health check responds: `GET /health`
- [ ] System diagnostics respond: `GET /api/v1/system/health`
- [ ] Services count shows all 5 services up
- [ ] Database connection status shows "connected"
- [ ] Python scripts available
- [ ] No service response times exceed 5 seconds
- [ ] Overall status is "healthy"

---

## 🎓 Next Steps

1. **Start the system**: `docker-compose up -d --build`
2. **Get a token**: Follow authentication section above
3. **Run diagnostics**: Call any endpoint above with your token
4. **Run Python tests**: `pytest integration/test_system_health.py -v`
5. **Monitor**: Use the Python monitoring script for continuous checks

---

## 📞 Support

For issues or questions, check:
- Endpoint responses in Swagger UI: `http://localhost:8000/docs`
- Docker logs: `docker-compose logs -f`
- Python test output: `pytest -vvs`

