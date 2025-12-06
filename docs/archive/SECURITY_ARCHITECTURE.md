# 🔐 Security Architecture - Document Processor Access

## Core Principle

**Port 8070 (Document Processor) is NOT exposed to the host machine.**

This is an intentional security design that ensures:
- ✅ All client access goes through the API Gateway
- ✅ Client authentication (user JWT) is validated first
- ✅ Service-to-service tokens never leave the internal network
- ✅ Complete audit trail through API Gateway
- ✅ Protection against unauthorized direct access

---

## Network Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         HOST MACHINE                             │
│                                                                  │
│  Postman / Client Application                                   │
│         │                                                        │
│         │ (User JWT)                                             │
│         │                                                        │
│         ▼                                                        │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │     API Gateway (Port 8000) ✅ EXPOSED                 │ │
│    │  • Validates user JWT                                   │ │
│    │  • Generates service JWT                                │ │
│    │  • Proxies requests to internal services                │ │
│    └─────────────────────────────────────────────────────────┘ │
│                         │                                        │
│                         │ Docker Network                         │
│         ┌───────────────┼───────────────────────┐               │
│         │               │                       │               │
│         ▼               ▼                       ▼               │
│    ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│    │   Auth      │  │   User      │  │   Document           │ │
│    │   Tokens    │  │ Management  │  │   Processor          │ │
│    │   (8001) ✅ │  │ (8010) ✅   │  │   (8070) ❌ HIDDEN   │ │
│    │  EXPOSED    │  │  EXPOSED    │  │   NOT EXPOSED        │ │
│    └─────────────┘  └─────────────┘  └──────────────────────┘ │
│         │               │                       │               │
│         └───────────────┼───────────────────────┘               │
│                         │ Internal Network Only                 │
│                         ▼                                        │
│              (Service JWT communication)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Ports

| Service | Port | Exposed | Access From | Purpose |
|---------|------|---------|-------------|---------|
| API Gateway | 8000 | ✅ YES | Host/Client | Single entry point |
| User Management | 8010 | ✅ YES | Host/Client | Registration, activation |
| Auth Tokens | 8001 | ✅ YES | Host/Client | Login, token validation |
| Python Internal Service | 8002 | ❌ NO | Internal Network Only | Via Gateway only |
| Java Internal Service | 8003 | ❌ NO | Internal Network Only | Via Gateway only |
| **Document Processor** | **8070** | **❌ NO** | **Internal Network Only** | **Via Gateway only** |

---

## Accessing Document Processor

### ✅ RECOMMENDED: Via API Gateway

**How it works:**
1. Client sends request to API Gateway with user JWT token
2. API Gateway validates user JWT
3. API Gateway generates service JWT internally
4. API Gateway proxies request to Document Processor with service JWT
5. Document Processor validates service JWT
6. Document Processor processes request
7. Response returned to client through Gateway

**Example from Postman (Section 9):**
```
GET http://localhost:8000/api/v1/documents/types
Header: Authorization: Bearer {user_jwt_token}
```

**Response:**
```json
[
  "BROKER_PORTFOLIO",
  "MUTUAL_FUND",
  "NPS_STATEMENT",
  "COMPANY_FINANCIAL_REPORT",
  "STOCK_PORTFOLIO",
  "NSE_INDICES"
]
```

---

### ❌ NOT ACCESSIBLE: Direct from Host

**Why not?**
```bash
$ curl http://localhost:8070/api/v1/documents/types
curl: (52) Empty reply from server
```

**Reason:** Port 8070 is not mapped in `docker-compose.yml`:
```yaml
am-document-processor:
  build: ...
  environment: ...
  networks:
    - am-network
  # ❌ NO "ports:" section = not accessible from host
```

**Verified Docker Compose Configuration:**
- ✅ API Gateway: `ports: ["8000:8000"]` → EXPOSED
- ✅ User Management: `ports: ["8010:8000"]` → EXPOSED
- ✅ Auth Tokens: `ports: ["8001:8001"]` → EXPOSED
- ❌ Document Processor: NO ports section → NOT EXPOSED

---

### 🧪 TESTING: From Within Docker Network (Internal Testing Only)

If you need to test Document Processor endpoints from within the Docker network (for debugging):

```bash
# From API Gateway container
docker exec am-am-api-gateway-1 python3 -c \
  "import urllib.request; \
   print(urllib.request.urlopen('http://am-document-processor:8070/api/v1/documents/types').read().decode())"
```

**Output:**
```json
["BROKER_PORTFOLIO", "MUTUAL_FUND", "NPS_STATEMENT", ...]
```

**Important Notes:**
- ⚠️ This uses internal Docker network URL (`am-document-processor:8070`)
- ⚠️ NOT accessible from regular host machine
- ⚠️ For internal testing/debugging only
- ⚠️ Should NOT be used in production workflows
- ✅ Clients should always use API Gateway

---

## Authentication Flows

### Flow 1: Client → API Gateway → Document Processor (Recommended)

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │ 1. Login with credentials
       ▼
┌──────────────────────────────────────┐
│   Auth Tokens Service (8001)         │
│   ✅ Validates credentials           │
│   ✅ Returns user JWT                │
└──────┬───────────────────────────────┘
       │ 2. User JWT
       ▼
┌──────────────────────────────────────┐
│   Client                             │
│   ✅ Stores JWT token                │
└──────┬───────────────────────────────┘
       │ 3. API request with JWT
       ▼
┌──────────────────────────────────────┐
│   API Gateway (8000)                 │
│   ✅ Validates user JWT              │
│   ✅ Generates service JWT           │
│   ✅ Proxies to Document Processor   │
└──────┬───────────────────────────────┘
       │ 4. Service JWT (internal network)
       ▼
┌──────────────────────────────────────┐
│   Document Processor (8070)          │
│   ✅ Validates service JWT           │
│   ✅ Processes request               │
│   ✅ Returns result                  │
└──────────────────────────────────────┘
```

**Security Properties:**
- ✅ Client authenticates as user (not service)
- ✅ Service tokens never exposed to client
- ✅ Service tokens never leave internal network
- ✅ Complete audit trail
- ✅ Defense in depth

---

### Flow 2: Service-to-Service (Internal Only)

```
API Gateway ──(service JWT)──> Document Processor
```

**Key Points:**
- ✅ Uses INTERNAL_JWT_SECRET (different from user JWT secret)
- ✅ Only accessible within Docker network
- ✅ Includes service_id and user_id in token
- ✅ Short expiration (15 minutes)

**Token Structure:**
```json
{
  "user_id": "uuid-of-authenticated-user",
  "service_id": "document-processor",
  "type": "service",
  "exp": 1234567890,
  "iat": 1234567800
}
```

---

## JWT Configuration

### Environment Variables

**Exposed (used by API Gateway):**
```bash
JWT_SECRET=jwt-super-secret-signing-key-change-in-production-must-be-32chars-minimum-xyz
JWT_ALGORITHM=HS256
```

**Internal (used for service-to-service):**
```bash
INTERNAL_JWT_SECRET=internal-service-super-secret-key-32chars-minimum-change-in-prod
```

**Important:**
- ⚠️ Change these secrets in production
- ⚠️ Use strong random strings (32+ characters)
- ⚠️ Keep INTERNAL_JWT_SECRET secure (never expose)
- ✅ Stored in `.env` file (not in repository)
- ✅ Passed to services via docker-compose environment

---

## Document Processor Endpoints

### Public Endpoints (No Authentication)

```
GET /api/v1/documents/types
├─ Access: ✅ Via API Gateway (recommended)
├─ Access: 🧪 Direct from Docker network (testing)
├─ Access: ❌ NOT from host machine
├─ Authentication: ❌ Not required
├─ Returns: List of supported document types
└─ Example: ["BROKER_PORTFOLIO", "MUTUAL_FUND", ...]

GET /actuator/health
├─ Access: ✅ Via API Gateway
├─ Access: 🧪 Direct from Docker network
├─ Access: ❌ NOT from host machine
├─ Authentication: ❌ Not required
└─ Returns: Service health status
```

### Protected Endpoints (Service JWT Required)

```
POST /api/v1/documents/process
├─ Access: ✅ Via API Gateway only (recommended)
├─ Access: ❌ NOT from host machine
├─ Authentication: ✅ Service JWT required
├─ Requires: Valid service token
├─ Returns: Processing result with process_id
└─ Errors: 401 if token invalid, 400 if data invalid

POST /api/v1/documents/batch-process
├─ Access: ✅ Via API Gateway only
├─ Access: ❌ NOT from host machine
├─ Authentication: ✅ Service JWT required
└─ Returns: List of processing results

GET /api/v1/documents/status/{processId}
├─ Access: ✅ Via API Gateway only
├─ Access: ❌ NOT from host machine
├─ Authentication: ✅ Service JWT required
└─ Returns: Current status of processing request
```

---

## Security Checklist

- ✅ Port 8070 not exposed in docker-compose.yml
- ✅ Document Processor has SecurityConfig.java
- ✅ Public endpoints explicitly allowed in SecurityConfig
- ✅ Protected endpoints validated in controller
- ✅ JwtValidator validates service tokens
- ✅ INTERNAL_JWT_SECRET is different from JWT_SECRET
- ✅ Service tokens have short expiration (15 min)
- ✅ User tokens have longer expiration (1-2 hours)
- ✅ API Gateway validates user tokens
- ✅ API Gateway generates service tokens
- ✅ Service-to-service tokens not exposed to clients
- ✅ Complete audit trail through API Gateway

---

## Testing in Postman

### Section 9: Via API Gateway ✅ (RECOMMENDED)
- Use these endpoints for all client access
- Requires user JWT token
- API Gateway handles service JWT generation
- Most secure approach

### Section 10: Internal Testing Only 🧪
- For debugging/testing from within Docker network
- Not for production use
- Port 8070 not accessible from host
- Use Docker commands to test if needed

---

## Common Issues & Solutions

### ❌ Issue: Connection Refused on Port 8070
```
curl: (111) Connection refused
curl: (52) Empty reply from server
```

**Solution:** This is correct! Port 8070 is intentionally not exposed.
Use API Gateway instead:
```bash
# ❌ Wrong
curl http://localhost:8070/api/v1/documents/types

# ✅ Correct
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/documents/types
```

### ❌ Issue: 401 Unauthorized from Document Processor

**Possible causes:**
1. Service token invalid (signature mismatch)
   - Check INTERNAL_JWT_SECRET matches across services
   
2. Service token expired
   - Service tokens expire after 15 minutes
   - Generate new token via API Gateway
   
3. Token not in proper format
   - Must be: `Bearer {token}` (with space)
   - Check Authorization header

**Solution:** Use API Gateway which handles token generation:
```bash
# Let Gateway generate service token
curl -H "Authorization: Bearer $USER_TOKEN" \
  http://localhost:8000/api/v1/documents/types
```

### ❌ Issue: 415 Unsupported Media Type

**Cause:** Wrong Content-Type or multipart form data format

**Solution:** Use Postman "form-data" body type for POST requests

---

## Configuration Files

**Docker Compose Configuration:**
- Location: `am/docker-compose.yml`
- Status: ✅ Correct (port 8070 not mapped)

**Java Security Configuration:**
- Location: `AM-Repos/am-document-processor/src/main/java/org/am/mypotrfolio/config/SecurityConfig.java`
- Purpose: ✅ Configures Spring Security for public/protected endpoints

**JWT Validator:**
- Location: `AM-Repos/am-document-processor/src/main/java/org/am/mypotrfolio/security/JwtValidator.java`
- Purpose: ✅ Validates service tokens from API Gateway

**JWT Configuration:**
- Location: `AM-Repos/am-document-processor/src/main/java/org/am/mypotrfolio/config/JwtConfig.java`
- Purpose: ✅ Reads JWT secrets from environment

---

## Verification

To verify the security architecture is correctly implemented:

```bash
# 1. Verify port 8070 is not exposed
cd /Users/munishm/Documents/auth-test-3/am
docker-compose ps | grep document-processor
# Should show: no port mapping (just 8070/tcp, not 8070:8070)

# 2. Verify port is not accessible from host
curl http://localhost:8070/actuator/health
# Should fail with connection error

# 3. Verify access through API Gateway works
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/tokens \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"Test123!"}' | jq -r '.access_token')

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/documents/types
# Should return: ["BROKER_PORTFOLIO", "MUTUAL_FUND", ...]
```

---

## Summary

✅ **Document Processor is secure and properly integrated:**
- Port 8070 is NOT exposed to the host ✓
- All client access goes through API Gateway (port 8000) ✓
- Two-tier JWT authentication system ✓
- Service tokens never exposed to clients ✓
- Complete audit trail through API Gateway ✓
- Spring Security properly configured ✓

**ALWAYS use API Gateway for client access. Port 8070 should never be accessed directly from the host machine.**
