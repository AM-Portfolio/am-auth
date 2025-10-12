# Development Guide

## Getting Started

### Prerequisites
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Python** 3.11+
- **Java** 17+ (for Java service)
- **Git**
- **Postman** (optional, for API testing)

### Initial Setup

1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd auth-test
   ```

2. **Create environment file**:
   ```bash
   cd am
   cp .env.example .env.docker
   # Edit .env.docker with your settings
   ```

3. **Start services**:
   ```bash
   docker-compose up -d --build
   ```

4. **Verify**:
   ```bash
   docker-compose ps
   ```

## Project Structure

```
auth-test/
├── am/
│   ├── docker-compose.yml           # Orchestration
│   ├── .env.docker                  # Environment variables
│   │
│   ├── am-api-gateway/              # API Gateway Service
│   │   ├── main.py                  # FastAPI app
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── api/v1/endpoints/        # Endpoint definitions
│   │   ├── core/                    # Config, auth
│   │   └── middleware/              # Rate limiting, logging
│   │
│   ├── am-user-management/          # User Management Service
│   │   ├── main.py
│   │   ├── modules/                 # Domain modules
│   │   ├── shared_infra/            # Shared infrastructure
│   │   └── tests/                   # Unit tests
│   │
│   ├── am-auth-tokens/              # Auth Service
│   │   ├── main.py
│   │   ├── app/                     # Application code
│   │   └── shared_infra/            # Config
│   │
│   ├── am-python-internal-service/  # Python Internal
│   │   └── main.py
│   │
│   └── am-java-internal-service/    # Java Internal
│       ├── src/main/java/
│       └── pom.xml
│
├── docs/                            # Documentation
├── postman/                         # API collections
└── shared/                          # Shared utilities
    └── logging/                     # Centralized logging
```

## Development Workflow

### Working on API Gateway

1. **Make changes** to files in `am/am-api-gateway/`

2. **Rebuild service**:
   ```bash
   docker-compose up -d --build am-api-gateway
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f am-api-gateway
   ```

4. **Test changes**:
   ```bash
   curl http://localhost:8000/health
   ```

### Working on User Management

1. **Make changes** to files in `am/am-user-management/`

2. **Rebuild**:
   ```bash
   docker-compose up -d --build am-user-management
   ```

3. **Run tests**:
   ```bash
   docker exec -it am-am-user-management-1 pytest
   ```

### Adding New Endpoint

1. **Create endpoint file**:
   ```bash
   # am/am-api-gateway/api/v1/endpoints/my_feature.py
   ```

2. **Follow existing pattern**:
   ```python
   from fastapi import APIRouter, Depends
   from core.auth import get_current_user, CurrentUser
   
   router = APIRouter()
   
   @router.get("/my-feature")
   async def get_my_feature(
       current_user: CurrentUser = Depends(get_current_user)
   ):
       # Your logic here
       return {"message": "Hello from my feature"}
   ```

3. **Register router** in `main.py`:
   ```python
   from api.v1.endpoints import my_feature
   
   app.include_router(
       my_feature.router,
       prefix="/api/v1/my-feature",
       tags=["my-feature"]
   )
   ```

4. **Rebuild and test**:
   ```bash
   docker-compose up -d --build am-api-gateway
   curl http://localhost:8000/api/v1/my-feature \
     -H "Authorization: Bearer $TOKEN"
   ```

## Testing

### Unit Tests

**User Management Service**:
```bash
# Run all tests
docker exec -it am-am-user-management-1 pytest

# Run specific test file
docker exec -it am-am-user-management-1 pytest tests/test_user_service.py

# Run with coverage
docker exec -it am-am-user-management-1 pytest --cov=modules
```

### Integration Tests

**With Postman**:
1. Import collections from `postman/` directory
2. Set environment variables
3. Run collection tests

**With cURL**:
```bash
# See docs/QUICK_START.md for test sequence
```

### Load Testing

**Using Apache Bench**:
```bash
# Install ab
brew install apache-bench  # macOS

# Test API Gateway
ab -n 1000 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/documents
```

**Using k6**:
```javascript
// load-test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function() {
  let res = http.get('http://localhost:8000/health');
  check(res, { 'status is 200': (r) => r.status === 200 });
}
```

```bash
k6 run load-test.js
```

## Debugging

### View Logs

**All services**:
```bash
docker-compose logs -f
```

**Specific service**:
```bash
docker-compose logs -f am-api-gateway
docker-compose logs -f am-user-management
```

**Last N lines**:
```bash
docker-compose logs --tail=100 am-api-gateway
```

### Access Container Shell

```bash
# Python services
docker exec -it am-am-api-gateway-1 bash

# Java service
docker exec -it am-am-java-internal-service-1 bash
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it am-postgres-1 psql -U am_user -d am_db

# List tables
\dt

# Query users
SELECT * FROM users;

# Exit
\q
```

### Network Debugging

**Test internal service connectivity**:
```bash
# From API Gateway container
docker exec -it am-am-api-gateway-1 bash
curl http://am-python-internal-service:8002/health
curl http://am-java-internal-service:8003/health
```

## Code Style

### Python

**Follow PEP 8**:
```bash
# Install tools
pip install black isort flake8 mypy

# Format code
black .
isort .

# Lint
flake8 .

# Type check
mypy .
```

**Pre-commit hooks**:
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Java

**Follow Google Java Style**:
```bash
# Format with maven
mvn spotless:apply

# Check style
mvn spotless:check
```

## Environment Variables

### Development (.env.docker)

```bash
# JWT Configuration
JWT_SECRET=development-secret-change-in-production
JWT_ALGORITHM=HS256
INTERNAL_JWT_SECRET=internal-development-secret

# Database
DATABASE_URL=postgresql://am_user:am_password@postgres:5432/am_db
POSTGRES_USER=am_user
POSTGRES_PASSWORD=am_password
POSTGRES_DB=am_db

# Service URLs (internal Docker network)
AUTH_SERVICE_URL=http://auth-tokens:8001
USER_MANAGEMENT_URL=http://am-user-management:8000
PYTHON_SERVICE_URL=http://am-python-internal-service:8002
JAVA_SERVICE_URL=http://am-java-internal-service:8003

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_FORMAT=json
LOG_CONSOLE=true
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Production

**NEVER commit production secrets!**

Use:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Kubernetes Secrets

## Database Migrations

### Alembic (Python services)

```bash
# Create migration
docker exec -it am-am-user-management-1 alembic revision --autogenerate -m "Add new field"

# Apply migration
docker exec -it am-am-user-management-1 alembic upgrade head

# Rollback
docker exec -it am-am-user-management-1 alembic downgrade -1
```

## Performance Optimization

### Database Indexing

```sql
-- Add index for frequently queried fields
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
```

### Caching

```python
# Add Redis caching (future)
from redis import Redis
cache = Redis(host='redis', port=6379)

@router.get("/documents")
async def get_documents(user_id: str):
    # Check cache first
    cached = cache.get(f"docs:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from database
    docs = fetch_documents(user_id)
    
    # Cache for 5 minutes
    cache.setex(f"docs:{user_id}", 300, json.dumps(docs))
    return docs
```

### Connection Pooling

```python
# Database connection pool (already configured)
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build services
        run: docker-compose build
      
      - name: Run tests
        run: docker-compose run am-user-management pytest
      
      - name: Lint
        run: docker-compose run am-api-gateway flake8 .

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Recreate database
docker-compose down -v
docker-compose up -d postgres
```

### Service Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Out of Disk Space

```bash
# Remove unused images
docker system prune -a

# Remove volumes
docker volume prune
```

## Best Practices

### 1. Never Commit Secrets
- Use `.env` files (gitignored)
- Use secret management tools
- Rotate secrets regularly

### 2. Write Tests
- Unit tests for business logic
- Integration tests for APIs
- Maintain >80% coverage

### 3. Document Changes
- Update README when adding features
- Document API changes
- Keep CHANGELOG.md updated

### 4. Use Type Hints
```python
def get_user(user_id: str) -> User:
    ...
```

### 5. Handle Errors Gracefully
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail="Operation failed")
```

### 6. Log Appropriately
- INFO: Important events
- WARNING: Unusual but handled
- ERROR: Failures requiring attention
- DEBUG: Detailed troubleshooting info

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Python Best Practices](https://docs.python-guide.org/)
- [RESTful API Design](https://restfulapi.net/)

---

**Happy Coding! 🚀**

Questions? Check the docs or ask the team!
