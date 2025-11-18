# 🔒 Security Architecture - Complete Guide

> **Consolidated from:** SECURITY_ARCHITECTURE.md + SECURITY_QUICK_REFERENCE.md

## Quick Answer

**Even with a valid JWT token, Postman cannot connect to internal services because the ports are not exposed to your computer.**

```
Your Computer (Postman) → 🚫 BLOCKED 🚫 → Docker Internal Network
                          No port mapping
```

---

## 🏗️ Two-Layer Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR COMPUTER (Outside Docker Network)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Postman / Browser                                   │  │
│  │  Authorization: Bearer eyJhbGc...                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ✅ Can access: http://localhost:8000 (API Gateway)        │
│  ✅ Can access: http://localhost:8010 (User Management)    │
│  ✅ Can access: http://localhost:8001 (Auth Tokens)        │
│  ❌ CANNOT access: http://localhost:8002 (Python Service)  │
│  ❌ CANNOT access: http://localhost:8003 (Java Service)    │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    🚧 BLOCKED BY LAYER 1
                    (No port mapping)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  DOCKER INTERNAL NETWORK (am-network)                       │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ API Gateway      │  │ User Management  │               │
│  │ Port: 8000       │  │ Port: 8010       │               │
│  │ MAPPED: ✅       │  │ MAPPED: ✅       │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ Python Service   │  │ Java Service     │               │
│  │ Port: 8002       │  │ Port: 8003       │               │
│  │ MAPPED: ❌       │  │ MAPPED: ❌       │               │
│  │ (Internal Only)  │  │ (Internal Only)  │               │
│  │ 🔑 JWT Required  │  │ 🔑 JWT Required  │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Security Layers Explained

### 🚧 Layer 1: Network Isolation
- **What:** Docker containers without port mappings
- **Blocks:** All external connections
- **When:** BEFORE token is checked
- **Result:** Connection Refused

### 🔑 Layer 2: JWT Authentication  
- **What:** Token validation middleware
- **Blocks:** Unauthorized internal requests
- **When:** ONLY if Layer 1 allows connection
- **Result:** 401 Unauthorized (if no token) or 200 OK (if valid)

---

## 🔍 What Happens Step-by-Step

### ❌ When You Call from Postman:

```bash
GET http://localhost:8002/internal/service-info
Authorization: Bearer eyJhbGc...

Step 1: Your computer tries to connect to localhost:8002
Step 2: Operating system: Port 8002 not found on host
Step 3: Connection refused ❌
Step 4: Request never reaches container
        → Authorization header never processed
        → JWT never validated
```

### ✅ When Called from Docker Network:

```bash
# From API Gateway or another container:
GET http://am-python-internal-service:8002/internal/service-info
Authorization: Bearer eyJhbGc...

Step 1: Container resolves hostname via Docker network ✅
Step 2: TCP connection established (Layer 1 passed) ✅
Step 3: Request reaches FastAPI application ✅
Step 4: JWT middleware validates token (Layer 2) ✅
Step 5: Request processed → 200 OK ✅
```

---

## 📋 Docker Compose Configuration

### ✅ Public Services (Externally Accessible):

```yaml
am-api-gateway:
  ports:
    - "8000:8000"  # ← Port mapping: host:container
  # You CAN access via localhost:8000
```

### ❌ Internal Services (Network Isolated):

```yaml
am-python-internal-service:
  # NO ports: section!
  # Port 8002 only exists INSIDE Docker network
  # You CANNOT access via localhost:8002
```

---

## 🎭 Real-World Analogy: The Bank Vault

**Layer 1: Physical Building Security (Network Isolation)**
- The vault is in a secure room with no public entrance
- Even if you have the key, you can't reach the door
- **Postman = Standing outside trying to use the key**

**Layer 2: Vault Lock (JWT Authentication)**
- IF you get inside the building (via employee entrance)
- THEN you need the correct key (JWT token)
- **Docker network = Being inside with the key**

---

## 🛡️ Why Two Layers? (Defense in Depth)

1. **JWT Token Stolen?**
   - Attacker still can't access from outside ✅
   - Network isolation prevents external access ✅

2. **Network Firewall Bypassed?**
   - Attacker still needs valid JWT token ✅
   - Authentication blocks unauthorized access ✅

3. **Zero Trust Architecture**
   - Don't trust network alone ✅
   - Don't trust authentication alone ✅
   - Both required for access ✅

---

## 🧪 How to Test Internal Services

### Method 1: Via API Gateway (Recommended)

```bash
# 1. Get token
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Test123!"}'

# 2. Use API Gateway to access internal services
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Method 2: Test from Inside Docker

```bash
# Enter container
docker exec -it am-am-api-gateway-1 sh

# Test internal service
curl http://am-python-internal-service:8002/internal/service-info \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Method 3: Check Logs

```bash
docker-compose logs am-python-internal-service
docker-compose logs am-java-internal-service
```

---

## 📊 Service Access Matrix

| Service | External Access | Internal (No Token) | Internal (With Token) |
|---------|----------------|--------------------|-----------------------|
| API Gateway (8000) | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| User Management (8010) | ✅ Allowed | ✅ Allowed | ✅ Allowed |
| Auth Tokens (8001) | ✅ Allowed | ✅ Allowed (some) | ✅ Allowed |
| Python Service (8002) | ❌ **Connection Refused** | ❌ 401 Unauthorized | ✅ 200 OK |
| Java Service (8003) | ❌ **Connection Refused** | ❌ 401 Unauthorized | ✅ 200 OK |

---

## ❓ FAQ

**Q: Why can't I access port 8002/8003 with valid Authorization?**  
A: Layer 1 (network isolation) blocks before Layer 2 (JWT) can check your token.

**Q: Is this a bug?**  
A: No! This is intentional security design (defense in depth).

**Q: How do I test these services?**  
A: Use the API Gateway (port 8000) which has access to internal services.

**Q: Can I expose these ports for testing?**  
A: You could add port mappings, but it defeats the security purpose. Use API Gateway instead.

**Q: How do services communicate internally?**  
A: They use Docker hostnames:
- `http://am-python-internal-service:8002`
- `http://am-java-internal-service:8003`

---

## 🎓 Key Takeaways

1. ✅ **Authorization header is correct** - token is valid
2. ❌ **Connection is blocked** - network isolation working
3. 🔒 **Two-layer security** - both layers required
4. 🎯 **This is intentional** - not a bug, it's a feature
5. 🌐 **Use API Gateway** - it has access to internal services
6. 🔐 **57% attack surface reduction** - 3 vs 7 exposed services

---

## 📚 Related Documentation

- `.github/copilot-instructions.md` - AI agent development guide
- `docs/ARCHITECTURE.md` - Full system design
- `docs/SECURITY.md` - Security patterns
- `docs/QUICK_START.md` - Getting started guide

---

**🎉 Your authentication system is working perfectly! The "Connection Refused" from Postman proves Layer 1 security is protecting your internal services.**
