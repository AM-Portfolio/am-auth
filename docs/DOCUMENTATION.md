# 📚 AM Authentication System - Documentation Index

Complete guide to all documentation for the authentication microservices system.

---

## 🎯 Start Here - By Use Case

### 👤 I Want to Use the API
→ **Start with:** `/postman/QUICK_REFERENCE.md` (5 minutes)  
**Then:** Import `/postman/AM-Complete-API-Collection.postman_collection.json`

### 🏗️ I Want to Understand the Architecture
→ **Read:** `/docs/ARCHITECTURE.md` (15 minutes)  
**Then:** `/docs/SECURITY.md` for security details  
**Then:** `/.github/copilot-instructions.md` for development patterns

### 🧪 I Want to Test Everything
→ **Run:** `/am/test_all.sh` (automated tests)  
**Guide:** `/docs/TESTING.md` (comprehensive testing guide)  
**Postman:** `/postman/POSTMAN_COMPLETE_GUIDE.md` (manual testing)

### 🔑 I Need Password Reset Feature
→ **Read:** `/FEATURE_PASSWORD_RESET.md` (complete guide)  
**Test:** Section 3 in `/docs/TESTING.md`  
**Postman:** Group 4 in `/postman/AM-Complete-API-Collection.postman_collection.json`

### 🚀 I Want to Deploy to Production
→ **Read:** `/docs/QUICK_START.md` (setup guide)  
**Then:** See deployment section in `/.github/copilot-instructions.md`  
**Reference:** `/docs/SECURITY.md` for security checklist

### 💻 I'm a Developer Adding Features
→ **Start:** `/.github/copilot-instructions.md` (200+ lines of patterns)  
**Architecture:** `/docs/ARCHITECTURE.md` (system design)  
**Code Examples:** Each service README

### 🐛 Something's Not Working
→ **Check:** `/docs/QUICK_START.md` → Troubleshooting section  
**Debug Guide:** `/postman/POSTMAN_COMPLETE_GUIDE.md` → Troubleshooting section  
**Test:** Run `/am/test_all.sh` to verify system

---

## 📖 Documentation Files

### Core Documentation (Root Level)

| File | Purpose | Length |
|------|---------|--------|
| **`/.github/copilot-instructions.md`** | Development patterns & architecture | 200+ lines |
| **`/FEATURE_PASSWORD_RESET.md`** | Complete password reset guide | 400+ lines |
| **`/DOCUMENTATION.md`** | This file - documentation index | - |

### API & Testing

| File | Purpose | Read Time |
|------|---------|-----------|
| **`/postman/README.md`** | Postman overview & quick links | 5 min |
| **`/postman/QUICK_REFERENCE.md`** | 30-second setup & common tasks | 5 min |
| **`/postman/POSTMAN_COMPLETE_GUIDE.md`** | Comprehensive Postman reference | 20 min |
| **`/postman/AM-Complete-API-Collection.postman_collection.json`** | Ready-to-import collection (27 requests) | - |

### System Documentation (docs/ directory)

| File | Purpose | Read Time |
|------|---------|-----------|
| **`/docs/ARCHITECTURE.md`** | System design & microservices | 15 min |
| **`/docs/QUICK_START.md`** | 5-minute setup guide | 5 min |
| **`/docs/SECURITY.md`** | Security patterns & checklist | 15 min |
| **`/docs/TESTING.md`** | Comprehensive testing guide | 20 min |

### Service-Specific Documentation (am/service directories)

| Service | Files |
|---------|-------|
| **API Gateway** | `am/am-api-gateway/README.md`, `QUICK_START.md` |
| **User Management** | `am/am-user-management/README.md` |
| **Auth Tokens** | `am/am-auth-tokens/README.md`, `ENVIRONMENT_GUIDE.md` |
| **Python Internal** | `am/am-python-internal-service/` (implementation docs) |
| **Java Internal** | `am/am-java-internal-service/` (Spring Boot patterns) |

---

## 🔍 Documentation Map

### By Topic

**Microservices Architecture**
- Start: `/docs/ARCHITECTURE.md`
- Deep dive: `/.github/copilot-instructions.md` → "Architecture Overview" section
- Security: `/docs/SECURITY.md` → "Service Communication Flow"

**API Gateway Pattern**
- Explained: `/docs/ARCHITECTURE.md` → "API Gateway Pattern"
- Implementation: `/.github/copilot-instructions.md` → "Service Communication Flow"
- Adding endpoints: `/.github/copilot-instructions.md` → "Adding New Endpoints"

**JWT Authentication**
- Two-tier pattern: `/.github/copilot-instructions.md` → "Two JWT Secrets Pattern"
- Security: `/docs/SECURITY.md` → "JWT Security"
- Testing: `/docs/TESTING.md` → "Authentication Testing"

**Password Reset Feature**
- Complete guide: `/FEATURE_PASSWORD_RESET.md`
- Implementation: `/FEATURE_PASSWORD_RESET.md` → "Implementation Details"
- Testing: `/FEATURE_PASSWORD_RESET.md` → "Testing Guide"
- Postman: `/postman/POSTMAN_COMPLETE_GUIDE.md` → "Password Reset 3-Step Guide"

**Testing & Validation**
- Automated: `/am/test_all.sh` + `/docs/TESTING.md`
- Postman manual: `/postman/POSTMAN_COMPLETE_GUIDE.md`
- Security testing: `/postman/POSTMAN_COMPLETE_GUIDE.md` → "Security Testing Group"
- Rate limiting: `/postman/POSTMAN_COMPLETE_GUIDE.md` → "Rate Limiting Group"

**Logging & Monitoring**
- Shared logging: `/.github/copilot-instructions.md` → "Centralized Logging"
- Implementation: `/shared/logging/` directory
- Configuration: `/am/.env.docker`

**Database & ORM**
- SQLAlchemy patterns: `/.github/copilot-instructions.md` → "Dependency Injection Standard"
- Schema: `/docs/ARCHITECTURE.md` → "Database Schema"
- Migrations: Auto-handled on service startup

**Docker & Deployment**
- Development setup: `/docs/QUICK_START.md`
- Docker Compose: `/am/docker-compose.yml`
- Production: `/.github/copilot-instructions.md` → "Deployment Workflow"

---

## ✅ Quick Checklists

### Pre-Development Checklist
- [ ] Read `/.github/copilot-instructions.md` (30 min)
- [ ] Read `/docs/ARCHITECTURE.md` (15 min)
- [ ] Run `/am/test_all.sh` to verify setup (5 min)
- [ ] Review password reset at `/FEATURE_PASSWORD_RESET.md` (if relevant)

### Before Deploying
- [ ] Run all tests: `/am/test_all.sh`
- [ ] Review security checklist: `/docs/SECURITY.md` → end of file
- [ ] Check logs format: `/am/.env.docker` → `LOG_FORMAT`
- [ ] Verify all environment variables set
- [ ] Test health endpoints via `/postman/` collection

### Testing a New Feature
- [ ] Write unit tests (see `/docs/TESTING.md`)
- [ ] Add Postman request (see `/postman/POSTMAN_COMPLETE_GUIDE.md`)
- [ ] Run integration tests
- [ ] Update relevant documentation
- [ ] Add security tests if handling auth/passwords

### Password Reset Related Tasks
- [ ] Understanding feature: `/FEATURE_PASSWORD_RESET.md` → "Quick Start"
- [ ] Testing manually: `/FEATURE_PASSWORD_RESET.md` → "Manual Testing"
- [ ] Testing via Postman: `/postman/POSTMAN_COMPLETE_GUIDE.md` → "Password Reset 3-Step Guide"
- [ ] Debugging: `/FEATURE_PASSWORD_RESET.md` → "Troubleshooting"

---

## 🗂️ File Organization

```
/
├── .github/
│   └── copilot-instructions.md        ← Development patterns
├── docs/
│   ├── ARCHITECTURE.md                ← System design
│   ├── QUICK_START.md                 ← 5-minute setup
│   ├── SECURITY.md                    ← Security patterns
│   ├── TESTING.md                     ← Complete testing guide
│   └── archive/                       ← Old/deprecated docs
├── postman/
│   ├── README.md                      ← Postman overview
│   ├── QUICK_REFERENCE.md             ← 30-sec setup & common tasks
│   ├── POSTMAN_COMPLETE_GUIDE.md      ← Comprehensive guide
│   └── AM-Complete-API-Collection.json ← Ready-to-import collection
├── am/
│   ├── test_all.sh                    ← Run all tests
│   ├── docker-compose.yml             ← Service orchestration
│   ├── am-api-gateway/
│   ├── am-user-management/
│   ├── am-auth-tokens/
│   ├── am-python-internal-service/
│   └── am-java-internal-service/
├── shared/
│   ├── auth/                          ← JWT utilities
│   └── logging/                       ← Centralized logging
├── FEATURE_PASSWORD_RESET.md          ← Password reset feature guide
├── DOCUMENTATION.md                   ← This file
├── README.md                          ← Project overview
└── pyproject.toml                     ← Python project config
```

---

## 🚀 Common Workflows

### Workflow 1: Get Up and Running (15 minutes)
1. Read: `/docs/QUICK_START.md`
2. Start: `cd am && docker-compose up -d --build`
3. Verify: `docker-compose ps` (all should be UP)
4. Test: Run `/am/test_all.sh`
5. Access API: Via `/postman/` collection

### Workflow 2: Test Password Reset (10 minutes)
1. Start services: `cd am && docker-compose up -d --build`
2. Quick read: `/FEATURE_PASSWORD_RESET.md` → "Quick Start"
3. Manual test: Follow steps in `/FEATURE_PASSWORD_RESET.md`
4. Postman test: Import collection, run Group 4
5. Check logs: `docker-compose logs am-user-management | grep -i reset`

### Workflow 3: Add New API Endpoint (1-2 hours)
1. Read patterns: `/.github/copilot-instructions.md` → "Adding New Endpoints"
2. Review example: `am/am-api-gateway/api/v1/endpoints/documents.py`
3. Create endpoint file
4. Register in main.py
5. Add Postman request
6. Add tests to `/docs/TESTING.md`

### Workflow 4: Debug a 401 Error (5 minutes)
1. Check: Is user activated? (not just registered)
2. Check: Token format correct? (`Authorization: Bearer <token>`)
3. Check: Token expired? (default 1 hour)
4. Check: User exists? `/postman/` → Run Health Check first
5. See: `/postman/POSTMAN_COMPLETE_GUIDE.md` → Troubleshooting

### Workflow 5: Deploy to Production (1-2 hours)
1. Read: `/docs/QUICK_START.md` → Production section
2. Review: `/docs/SECURITY.md` → "Security Checklist"
3. Check: `/.github/copilot-instructions.md` → "Environment Variables"
4. Test: Run `/am/test_all.sh` against production URLs
5. Monitor: Check logs and metrics post-deployment

---

## 📊 Documentation Statistics

| Category | Files | Lines | Status |
|----------|-------|-------|--------|
| Core Documentation | 1 | 400+ | ✅ Complete |
| Postman Guides | 3 | 1,100+ | ✅ Complete |
| System Docs | 4 | 2,000+ | ✅ Complete |
| Feature Docs | 1 | 400+ | ✅ Complete |
| Dev Instructions | 1 | 200+ | ✅ Complete |
| Service READMEs | 5 | 1,500+ | ✅ Complete |
| **TOTAL** | **15** | **5,600+** | ✅ Complete |

---

## 🆘 Getting Help

### Problem: Can't get services running
**Solution:**
1. Check: `cd am && docker-compose ps`
2. If any are DOWN: `docker-compose logs <service_name>`
3. Reference: `/docs/QUICK_START.md` → Troubleshooting
4. Reset: `docker-compose down && docker-compose up -d --build`

### Problem: Tests failing
**Solution:**
1. Run: `/am/test_all.sh` to see which tests fail
2. Read: `/docs/TESTING.md` for test details
3. Check: Specific test file in `am/tests/` directory
4. Debug: Use Postman collection to test endpoints manually

### Problem: Password reset not working
**Solution:**
1. Read: `/FEATURE_PASSWORD_RESET.md` → Troubleshooting
2. Check logs: `docker-compose logs am-user-management | grep -i reset`
3. Manual test: Follow steps in `/FEATURE_PASSWORD_RESET.md` → "Manual Testing"
4. Verify: Token in logs with: `docker-compose logs | grep "Reset token"`

### Problem: API returning 401/403 errors
**Solution:**
1. Check: `/postman/POSTMAN_COMPLETE_GUIDE.md` → "Security Testing Group"
2. Verify: User is activated (not just registered)
3. Check: Token format: `Authorization: Bearer <token>`
4. Test: With Postman collection, Group 2 (User Registration & Activation)

### Problem: Can't figure out how something works
**Solution:**
1. Check: Topic index in this file (DOCUMENTATION.md)
2. Find: Relevant documentation section
3. Search: Within that file for your specific question
4. Example: Use Postman collection to see working requests

---

## 🔄 Documentation Maintenance

### How to Update Docs
1. Find relevant file(s) in this index
2. Make changes
3. Update version number (if applicable)
4. Commit with clear message
5. Update related cross-references

### How to Report Issues
1. Check this index (DOCUMENTATION.md) for relevant doc
2. Read that doc completely
3. If still stuck, check Troubleshooting section
4. If documentation is unclear, note what's confusing
5. Reference specific lines/sections for clarity

### How to Add New Documentation
1. Identify topic and audience
2. Place in appropriate directory (see File Organization)
3. Add entry to this index (DOCUMENTATION.md)
4. Add cross-references in related files
5. Update relevant sections with "See Also:" links

---

## 📝 Version History

| Date | Version | Changes |
|------|---------|---------|
| Nov 18, 2025 | 1.0.0 | Created consolidated DOCUMENTATION.md index |
| Nov 18, 2025 | - | Consolidated password reset docs into FEATURE_PASSWORD_RESET.md |
| Nov 18, 2025 | - | Updated postman/README.md as main Postman index |

---

## ✨ Navigation Tips

- **Use Ctrl/Cmd + F** to search within markdown files
- **Use Cmd + Click** (Mac) / Ctrl + Click (Windows) to follow links in VS Code
- **Read in order suggested** for each use case above
- **Start with QUICK_REFERENCE.md** if you're short on time
- **Use Postman collection** for hands-on testing
- **Check `.github/copilot-instructions.md`** for detailed development patterns

---

**Last Updated:** November 18, 2025 | **Status:** ✅ Complete | **Coverage:** All topics
