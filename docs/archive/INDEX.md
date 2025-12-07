# Documentation Index

## 📚 Core Documentation

### Getting Started
- **[README.md](../README.md)** - Project overview and quick start
- **[QUICK_START.md](./QUICK_START.md)** - Get up and running in 5 minutes
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design patterns

### Development
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Development workflow, testing, debugging
- **[API_GATEWAY_IMPLEMENTATION.md](./API_GATEWAY_IMPLEMENTATION.md)** - API Gateway implementation details

### Security
- **[SECURITY.md](./SECURITY.md)** - Security architecture, authentication, best practices

## 🔧 Service-Specific Documentation

### API Gateway
- [API Gateway README](../am/am-api-gateway/README.md) - Service overview
- [API Gateway Quick Start](../am/am-api-gateway/QUICK_START.md) - Testing guide

### User Management
- [User Management README](../am/am-user-management/README.md) - Service overview
- [Production Guide](../am/am-user-management/PRODUCTION_GUIDE.md) - Production deployment
- [Postman Guide](../am/am-user-management/POSTMAN_GUIDE.md) - API testing

### Auth Tokens
- [Auth Tokens README](../am/am-auth-tokens/README.md) - Service overview
- [Environment Guide](../am/am-auth-tokens/ENVIRONMENT_GUIDE.md) - Configuration
- [Postman Guide](../am/am-auth-tokens/POSTMAN_GUIDE.md) - API testing

## 🧪 Testing

### Postman Collections
- [Postman README](../postman/README.md) - Overview of API collections
- [Postman Quick Start](../postman/QUICK_START.md) - Quick testing guide
- [Endpoint Test Results](../postman/ENDPOINT_TEST_RESULTS.md) - Test status

### Collections
- `postman/User-Management-Service.postman_collection.json`
- `postman/Auth-Tokens-Service.postman_collection.json`

## 📖 Documentation Structure

```
docs/
├── INDEX.md                        # This file
├── QUICK_START.md                  # 5-minute setup guide
├── ARCHITECTURE.md                 # System architecture
├── SECURITY.md                     # Security documentation
├── DEVELOPMENT.md                  # Development guide
├── API_GATEWAY_IMPLEMENTATION.md   # API Gateway details
└── archive/                        # Old documentation (reference only)
    ├── CENTRALIZED_LOGGING_README.md
    ├── GOOGLE_OAUTH_IMPLEMENTATION.md
    ├── GOOGLE_OAUTH_STATUS.md
    ├── LOGGING_IMPLEMENTATION_SUMMARY.md
    ├── SECURITY_ARCHITECTURE.md
    ├── SECURITY_QUICK_REFERENCE.md
    ├── SERVICE_TO_SERVICE_AUTH_PROMPT.md
    ├── USER_STATUS_MANAGEMENT.md
    └── replit.md
```

## 🎯 Documentation by Use Case

### I want to...

#### ...understand the system
1. Read [README.md](../README.md) for overview
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for design
3. Check [SECURITY.md](./SECURITY.md) for security model

#### ...get started quickly
1. Follow [QUICK_START.md](./QUICK_START.md)
2. Use [Postman Quick Start](../postman/QUICK_START.md)
3. Test with provided collections

#### ...develop new features
1. Read [DEVELOPMENT.md](./DEVELOPMENT.md)
2. Review [API Gateway README](../am/am-api-gateway/README.md)
3. Check existing endpoints for patterns

#### ...deploy to production
1. Review [User Management Production Guide](../am/am-user-management/PRODUCTION_GUIDE.md)
2. Check [SECURITY.md](./SECURITY.md) for security checklist
3. Follow [DEVELOPMENT.md](./DEVELOPMENT.md) CI/CD section

#### ...test the APIs
1. Import Postman collections from `postman/` directory
2. Follow [Postman README](../postman/README.md)
3. Use [QUICK_START.md](./QUICK_START.md) for cURL examples

#### ...understand authentication
1. Read [SECURITY.md](./SECURITY.md) authentication section
2. Review [Auth Tokens README](../am/am-auth-tokens/README.md)
3. Check [API Gateway Implementation](./API_GATEWAY_IMPLEMENTATION.md)

#### ...troubleshoot issues
1. Check logs: `docker-compose logs -f`
2. Review [DEVELOPMENT.md](./DEVELOPMENT.md) troubleshooting section
3. Test health endpoints: `curl http://localhost:8000/health`

## 📊 Service Ports Reference

| Service | Port | Access | Documentation |
|---------|------|--------|---------------|
| API Gateway | 8000 | Public | [README](../am/am-api-gateway/README.md) |
| User Management | 8010 | Public | [README](../am/am-user-management/README.md) |
| Auth Tokens | 8001 | Public | [README](../am/am-auth-tokens/README.md) |
| Python Service | 8002 | Internal | N/A |
| Java Service | 8003 | Internal | N/A |
| PostgreSQL | 5432 | Internal | N/A |

## 🔍 Key Concepts

### API Gateway Pattern
Single entry point for all client requests. See:
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [API Gateway README](../am/am-api-gateway/README.md)

### Service Mesh
Internal services communicate via Docker network. See:
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Service Communication Matrix
- [SECURITY.md](./SECURITY.md) - Network Isolation

### JWT Authentication
Two-token system: User JWT → Service JWT. See:
- [SECURITY.md](./SECURITY.md) - Authentication Flow
- [Auth Tokens README](../am/am-auth-tokens/README.md)

### Rate Limiting
100 requests per 60 seconds per IP. See:
- [API Gateway README](../am/am-api-gateway/README.md) - Rate Limiting
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Rate Limiting Architecture

### RBAC (Role-Based Access Control)
Users have roles (user, admin, service). See:
- [SECURITY.md](./SECURITY.md) - RBAC Section
- [User Management README](../am/am-user-management/README.md)

## 🗂️ Archive

Old documentation has been moved to `docs/archive/` for reference:
- Historical implementation notes
- Previous security architectures
- Legacy OAuth implementations
- Old logging strategies

**Note**: Archive documents may be outdated. Refer to current documentation.

## 📝 Documentation Standards

### Writing Guidelines
1. **Use clear headings** - H2 for main sections, H3 for subsections
2. **Include code examples** - Show, don't just tell
3. **Add navigation** - Link to related docs
4. **Keep it updated** - Update docs when code changes
5. **Use emojis sparingly** - For visual organization only

### Markdown Style
```markdown
# H1 - Document title only
## H2 - Main sections
### H3 - Subsections
#### H4 - Details

**Bold** for emphasis
`code` for inline code
```code blocks``` for multi-line
- Lists for items
| Tables | for data |
```

### Code Examples
- Include language identifier: ```python, ```bash, ```json
- Show complete, runnable examples
- Include expected output
- Add comments for clarity

## 🔄 Keeping Docs Updated

### When to Update Documentation

**Code Changes**:
- New endpoints → Update API docs and Postman collections
- Configuration changes → Update DEVELOPMENT.md
- Architecture changes → Update ARCHITECTURE.md
- Security changes → Update SECURITY.md

**Process Changes**:
- Deployment process → Update Production guides
- Testing process → Update DEVELOPMENT.md
- Review process → Update README.md

### Documentation Checklist

When adding a new feature:
- [ ] Update README.md if it affects getting started
- [ ] Add/update service-specific README
- [ ] Update ARCHITECTURE.md if design changes
- [ ] Update SECURITY.md if security implications
- [ ] Add Postman collection examples
- [ ] Update DEVELOPMENT.md for dev workflow changes
- [ ] Add inline code comments
- [ ] Update version history

## 🤝 Contributing to Documentation

### Suggesting Improvements
1. Identify unclear sections
2. Propose specific improvements
3. Submit pull request with changes
4. Update INDEX.md if adding new docs

### Review Process
1. Check for accuracy
2. Verify code examples work
3. Ensure links are valid
4. Confirm formatting is consistent

## 📧 Contact

For documentation questions or improvements, contact the development team.

---

**Last Updated**: October 12, 2025  
**Documentation Version**: 2.0  
**Project Version**: v2.0.0
