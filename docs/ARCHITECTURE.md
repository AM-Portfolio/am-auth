# AM System Architecture

## Current Production-Ready Architecture

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                            INTERNET / CLIENTS                      ┃
┃              (Postman, Browser, Mobile Apps, etc.)                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                              │
                              │ HTTPS (443)
                              │
        ┏━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━┓
        ┃          EXPOSED SERVICES                  ┃
        ┃          (Docker Bridge Network)           ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                    │
        ┌───────────┼───────────────────┐
        │           │                   │
        ▼           ▼                   ▼
┏━━━━━━━━━━━━┓ ┏━━━━━━━━━━━━┓ ┏━━━━━━━━━━━━━━━━━┓
┃  API       ┃ ┃   User     ┃ ┃   Auth Tokens   ┃
┃  Gateway   ┃ ┃ Management ┃ ┃   Service       ┃
┃            ┃ ┃            ┃ ┃                 ┃
┃ Port: 8000 ┃ ┃ Port: 8010 ┃ ┃   Port: 8001    ┃
┃            ┃ ┃            ┃ ┃                 ┃
┃ Features:  ┃ ┃ Features:  ┃ ┃   Features:     ┃
┃ - Route    ┃ ┃ - Register ┃ ┃   - Login       ┃
┃ - Auth     ┃ ┃ - Activate ┃ ┃   - Validate    ┃
┃ - Rate Lmt ┃ ┃ - Profile  ┃ ┃   - Refresh     ┃
┃ - Logging  ┃ ┃ - RBAC     ┃ ┃   - Service JWT ┃
┗━━━━━┳━━━━━━┛ ┗━━━━━━━━━━━━┛ ┗━━━━━━━━━━━━━━━━━┛
      │
      │ Internal Docker Network
      │ (No External Ports)
      │
      ┌─────────────┴─────────────┐
      │                           │
      ▼                           ▼
┏━━━━━━━━━━━━━━━━━━┓    ┏━━━━━━━━━━━━━━━━━━┓
┃ Python Internal  ┃    ┃  Java Internal   ┃
┃    Service       ┃    ┃    Service       ┃
┃                  ┃    ┃                  ┃
┃  Port: 8002      ┃    ┃   Port: 8003     ┃
┃  (Internal Only) ┃    ┃  (Internal Only) ┃
┃                  ┃    ┃                  ┃
┃  Features:       ┃    ┃   Features:      ┃
┃  - Documents     ┃    ┃   - Reports      ┃
┃  - Processing    ┃    ┃   - Analytics    ┃
┃  - Business      ┃    ┃   - Business     ┃
┃    Logic         ┃    ┃     Logic        ┃
┗━━━━━━━━━━━━━━━━━━┛    ┗━━━━━━━━━━━━━━━━━━┛
      │                           │
      └────────────┬──────────────┘
                   │
                   ▼
         ┏━━━━━━━━━━━━━━━━━┓
         ┃    PostgreSQL    ┃
         ┃                  ┃
         ┃   Port: 5432     ┃
         ┃  (Database)      ┃
         ┗━━━━━━━━━━━━━━━━━┛
```

## Security Layers

### Layer 1: Network Isolation
```
Internet → Can Access:
  ✅ API Gateway (8000)
  ✅ User Management (8010) - For registration/login
  ✅ Auth Tokens (8001) - For token operations

Internet → CANNOT Access:
  ⛔ Python Internal Service (8002) - No port mapping
  ⛔ Java Internal Service (8003) - No port mapping
  ⛔ PostgreSQL (5432) - Behind network
```

### Layer 2: JWT Authentication
```
Client Request:
  Authorization: Bearer <user_jwt>
         │
         ▼
  API Gateway validates user JWT
         │
         ▼
  API Gateway generates service JWT
         │
         ▼
  Internal service validates service JWT
         │
         ▼
  Process request and return data
```

## Request Flow Example

### Getting User Documents

```
1. Client makes request:
   GET http://localhost:8000/api/v1/documents
   Header: Authorization: Bearer <user_token>

2. API Gateway (Port 8000):
   ├─ Rate limiter checks: 95/100 requests used
   ├─ Logging middleware: Start timer
   ├─ Authenticate user via auth-tokens service
   ├─ User validation success: user_id=123, roles=[user]
   ├─ Generate service token for Python service
   └─ Service token created with permissions=[read:documents]

3. API Gateway → Python Service (Internal):
   GET http://am-python-internal-service:8002/internal/documents
   Header: Authorization: Bearer <service_token>

4. Python Service (Port 8002):
   ├─ Validate service token
   ├─ Execute business logic
   ├─ Query database
   └─ Return documents: [{id: 1, name: "doc1.pdf"}]

5. API Gateway → Client:
   ├─ Log response time: 234ms
   ├─ Add headers: X-Process-Time, X-RateLimit-Remaining
   └─ Return response to client

Response:
{
  "documents": [
    {"id": 1, "name": "doc1.pdf", "size": "2.5MB"}
  ],
  "user_id": "123",
  "timestamp": "2024-01-01T12:00:00Z"
}

Headers:
  X-Process-Time: 0.234
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 94
  X-RateLimit-Reset: 1703001234
```

## Service Communication Matrix

| From Service | To Service | Network | Auth Required | Purpose |
|-------------|------------|---------|---------------|---------|
| Client | API Gateway | External | User JWT | All requests |
| Client | User Management | External | None (register), User JWT (update) | User operations |
| Client | Auth Tokens | External | User JWT | Token operations |
| API Gateway | Python Service | Internal | Service JWT | Documents API |
| API Gateway | Java Service | Internal | Service JWT | Reports API |
| API Gateway | Auth Service | Internal | User JWT | Validate/Generate tokens |
| All Services | PostgreSQL | Internal | DB credentials | Data persistence |
| Internal Services | Auth Service | Internal | Service JWT | Token validation |

## Rate Limiting Architecture

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   API Gateway           ┃
┃                         ┃
┃  Rate Limiter           ┃
┃  ┌──────────────────┐   ┃
┃  │ In-Memory Store  │   ┃
┃  │                  │   ┃
┃  │ {               │   ┃
┃  │  "192.168.1.1": │   ┃
┃  │    {            │   ┃
┃  │     count: 95,  │   ┃
┃  │     reset: 1703 │   ┃
┃  │    }            │   ┃
┃  │ }               │   ┃
┃  └──────────────────┘   ┃
┃                         ┃
┃  Limit: 100 req/60s     ┃
┃  Per: IP Address        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Note**: For production with multiple API Gateway instances, use Redis for distributed rate limiting.

## Monitoring Points

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃              Observability                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
    ┌──────┼──────┐
    │      │      │
    ▼      ▼      ▼
┌─────┐ ┌─────┐ ┌────────┐
│Logs │ │Metrics│ │Traces │
└─────┘ └──────┘ └────────┘

Current Implementation:
✅ Logs: Middleware logs all requests
   - Request: Method, path, IP, user
   - Response: Status, time, size

📝 Future: Metrics (Prometheus)
   - Request rate, error rate
   - Latency percentiles (p50, p95, p99)
   - Service availability

📝 Future: Traces (OpenTelemetry)
   - Request flow across services
   - Bottleneck identification
   - Dependency mapping
```

## Scalability Pattern

### Current (Development)
```
1 instance of each service on single Docker host
```

### Future (Production)
```
┏━━━━━━━━━━━━━━━━━━━━━━━┓
┃   Load Balancer        ┃
┃   (AWS ALB/NGINX)      ┃
┗━━━━━━━━━┳━━━━━━━━━━━━━┛
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐
│ Gateway │ │ Gateway │  (N instances)
│ Pod 1   │ │ Pod 2   │
└─────────┘ └─────────┘
    │           │
    └─────┬─────┘
          │
    ┌─────┴─────┬──────────┐
    │           │          │
    ▼           ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Python  │ │ Java   │ │Portfolio│
│Service │ │Service │ │Service  │
│(3 pods)│ │(3 pods)│ │(3 pods) │
└────────┘ └────────┘ └────────┘
```

## Security Comparison

### ❌ Before (Monolith / Exposed Services)
```
Internet
   │
   ├─→ User Service (8000)      ← Attack vector
   ├─→ Auth Service (8001)      ← Attack vector
   ├─→ Document Service (8002)  ← Attack vector
   ├─→ Report Service (8003)    ← Attack vector
   ├─→ Portfolio Service (8004) ← Attack vector
   ├─→ Trade Service (8005)     ← Attack vector
   └─→ Market Service (8006)    ← Attack vector

= 7 attack vectors
= 7 services to secure individually
= 7 rate limiters to configure
= 7 log sources to aggregate
```

### ✅ After (API Gateway Pattern)
```
Internet
   │
   ├─→ API Gateway (8000)       ← 1 attack vector
   │   └─→ [Internal Services]      (protected)
   │
   ├─→ User Service (8010)      ← For registration only
   └─→ Auth Service (8001)      ← For token operations

= 3 exposed services (vs 7)
= 1 primary entry point
= Centralized security
= Centralized logging
= Single rate limiter
```

## Attack Surface Reduction

```
Before API Gateway:
┌────────────────────────────────┐
│ Internet                       │
│  ↓ ↓ ↓ ↓ ↓ ↓ ↓               │
│ [All 7 services exposed]       │
│                                │
│ Attack Surface: ████████       │  100%
└────────────────────────────────┘

After API Gateway:
┌────────────────────────────────┐
│ Internet                       │
│  ↓ ↓ ↓                        │
│ [Only 3 services exposed]      │
│                                │
│ Attack Surface: ███            │   43%
└────────────────────────────────┘

Reduction: 57% fewer exposed services
```

## Token Flow Diagram

```
┌─────────┐                    ┌─────────────┐
│ Client  │                    │   Auth      │
│         │                    │   Tokens    │
└────┬────┘                    └──────┬──────┘
     │                                │
     │ 1. POST /login                 │
     │ (email, password)              │
     ├───────────────────────────────>│
     │                                │
     │ 2. Validate credentials        │
     │    Generate USER JWT           │
     │<───────────────────────────────┤
     │ {access_token: "eyJhbGc..."}   │
     │                                │
     │                                │
┌────┴────┐                    ┌──────┴──────┐
│ Client  │                    │  API        │
│         │                    │  Gateway    │
└────┬────┘                    └──────┬──────┘
     │                                │
     │ 3. GET /api/v1/documents       │
     │    Bearer: USER_JWT            │
     ├───────────────────────────────>│
     │                                │
     │                         ┌──────┴──────┐
     │                         │   Auth      │
     │                         │   Tokens    │
     │                         └──────┬──────┘
     │                                │
     │                         4. Validate USER_JWT
     │                         │
     │                         5. Generate SERVICE_JWT
     │                         │    (with permissions)
     │                         │
     │                         ┌──────┴──────┐
     │                         │   Python    │
     │                         │   Service   │
     │                         └──────┬──────┘
     │                                │
     │                         6. GET /internal/documents
     │                            Bearer: SERVICE_JWT
     │                         │
     │                         7. Validate SERVICE_JWT
     │                         │
     │                         8. Execute business logic
     │                         │
     │                         9. Return data
     │<────────────────────────┤
     │ {documents: [...]}             │
     │                                │
```

## Deployment Checklist

### ✅ Completed (Development)
- [x] API Gateway service created
- [x] Rate limiting implemented
- [x] JWT authentication flow
- [x] Service token generation
- [x] Internal services isolated
- [x] Logging middleware
- [x] Health checks
- [x] Documentation

### 📋 TODO (Production)
- [ ] SSL/TLS certificates
- [ ] Distributed rate limiting (Redis)
- [ ] Circuit breakers
- [ ] Response caching
- [ ] API versioning
- [ ] Monitoring dashboards
- [ ] Alert rules
- [ ] Load testing
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline

---

**This architecture provides:**
- ✅ Security through network isolation + JWT
- ✅ Scalability through independent services
- ✅ Observability through centralized logging
- ✅ Maintainability through clear separation of concerns
