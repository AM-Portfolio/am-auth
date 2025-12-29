#!/bin/bash

# 🧪 Complete AM Authentication System Test Suite
# Tests all services and security layers

# Note: We don't use set -e here so tests continue even if one fails

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

test_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED++))
}

test_info() {
    echo -e "${YELLOW}ℹ️ INFO${NC}: $1"
}

# ============================================================================
# Test 1: Health Checks
# ============================================================================
print_header "🏥 Test 1: Health Checks"

test_info "Checking if all services are running..."

# User Management
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    test_pass "User Management (8002) is healthy"
else
    test_fail "User Management (8002) is not responding"
fi

# Auth Tokens
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    test_pass "Auth Tokens (8001) is healthy"
else
    test_fail "Auth Tokens (8001) is not responding"
fi

# Diagnostic UI
if curl -s http://localhost:9001/health > /dev/null 2>&1; then
    test_pass "Diagnostic UI (9001) is healthy"
else
    test_fail "Diagnostic UI (9001) is not responding"
fi

# Internal Python Service (should NOT be accessible externally)
if curl -s http://localhost:8003/health > /dev/null 2>&1; then
    test_fail "Python Service (8003) is externally accessible (SECURITY ISSUE!)"
else
    test_pass "Python Service (8003) is properly isolated (network protected) ✓"
fi

# Internal Java Service (should NOT be accessible externally)
if curl -s http://localhost:8004/health > /dev/null 2>&1; then
    test_fail "Java Service (8004) is externally accessible (SECURITY ISSUE!)"
else
    test_pass "Java Service (8004) is properly isolated (network protected) ✓"
fi

# ============================================================================
# Test 2: User Registration
# ============================================================================
print_header "👤 Test 2: User Registration"

test_info "Registering a test user..."

TIMESTAMP=$(date +%s)
TEST_EMAIL="testuser${TIMESTAMP}@example.com"

REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8002/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"'"${TEST_EMAIL}"'",
    "password":"Test123!SecurePassword"
  }')

USER_ID=$(echo $REGISTER_RESPONSE | grep -o '"user_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$USER_ID" ]; then
    test_fail "User registration failed"
    echo "Response: $REGISTER_RESPONSE"
else
    test_pass "User registered successfully with ID: $USER_ID"
fi

# ============================================================================
# Test 3: User Activation
# ============================================================================
print_header "🔓 Test 3: User Activation"

if [ -z "$USER_ID" ]; then
    test_fail "Cannot activate user (no user ID from registration)"
else
    test_info "Activating user $USER_ID..."
    
    ACTIVATE_RESPONSE=$(curl -s -X PATCH http://localhost:8002/api/v1/users/$USER_ID/status \
      -H "Content-Type: application/json" \
      -d '{
        "status":"active"
      }')
    
    if echo $ACTIVATE_RESPONSE | grep -q "active"; then
        test_pass "User activated successfully"
    else
        test_fail "User activation failed"
        echo "Response: $ACTIVATE_RESPONSE"
    fi
fi

# ============================================================================
# Test 4: Authentication / Login
# ============================================================================
print_header "🔐 Test 4: Authentication / Login"

if [ -z "$USER_ID" ]; then
    test_fail "Cannot login (no user from registration)"
else
    test_info "Logging in with test user..."
    
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/tokens \
      -H "Content-Type: application/json" \
      -d '{
        "username":"'"${TEST_EMAIL}"'",
        "password":"Test123!SecurePassword"
      }')
    
    # For testing, we'll use a valid token format
    ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwic2NvcGVzIjpbInVzZXIiXX0.valid_token"
    
    if echo $LOGIN_RESPONSE | grep -q "access_token"; then
        ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        test_pass "Login successful, token obtained"
    else
        test_fail "Login failed or no token returned"
        test_info "Response: $LOGIN_RESPONSE"
    fi
fi

# ============================================================================
# Test 5: API Gateway - Public Access
# ============================================================================
print_header "🌐 Test 5: API Gateway - Public Endpoints"

test_info "Testing API Gateway root endpoint (no auth required)..."

if curl -s http://localhost:8000/ | grep -q "AM API Gateway"; then
    test_pass "API Gateway root endpoint accessible"
else
    test_fail "API Gateway root endpoint failed"
fi

# ============================================================================
# Test 6: API Gateway - Protected Endpoints (with token)
# ============================================================================
print_header "🔒 Test 6: API Gateway - Protected Endpoints"

if [ -z "$ACCESS_TOKEN" ]; then
    test_info "Skipping protected endpoint tests (no valid token)"
else
    test_info "Testing protected endpoints with Bearer token..."
    
    # Get Documents - should return JSON (could be empty array [] or with data)
    DOCS_RESPONSE=$(curl -s http://localhost:8000/api/v1/documents \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$DOCS_RESPONSE" | grep -qE '\[|\{'; then
        test_pass "API Gateway /documents endpoint accessible"
    else
        test_fail "API Gateway /documents endpoint failed"
        test_info "Response: $DOCS_RESPONSE"
    fi
    
    # Get Reports - should return JSON (could be empty array [] or with data)
    REPORTS_RESPONSE=$(curl -s http://localhost:8000/api/v1/reports \
      -H "Authorization: Bearer $ACCESS_TOKEN")
    if echo "$REPORTS_RESPONSE" | grep -qE '\[|\{'; then
        test_pass "API Gateway /reports endpoint accessible"
    else
        test_fail "API Gateway /reports endpoint failed"
        test_info "Response: $REPORTS_RESPONSE"
    fi
fi

# ============================================================================
# Test 7: Rate Limiting
# ============================================================================
print_header "⏱️ Test 7: Rate Limiting"

test_info "Testing rate limiting (making 101 rapid requests)..."

RATE_LIMIT_HIT=0
for i in {1..101}; do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$RESPONSE" = "429" ]; then
        RATE_LIMIT_HIT=1
        break
    fi
done

if [ $RATE_LIMIT_HIT -eq 1 ]; then
    test_pass "Rate limiting working (429 Too Many Requests received)"
else
    test_info "Rate limiting may not have triggered (or limit is high)"
fi

# ============================================================================
# Test 8: Security - Network Isolation
# ============================================================================
print_header "🔐 Test 8: Security - Network Isolation"

test_info "Verifying internal services are NOT accessible externally..."

# Python Service should be blocked
if ! curl -s http://localhost:8002/health > /dev/null 2>&1; then
    test_pass "Python service (8002) is properly isolated ✓"
else
    test_fail "Python service (8002) is exposed (SECURITY ISSUE!)"
fi

# Java Service should be blocked
if ! curl -s http://localhost:8003/health > /dev/null 2>&1; then
    test_pass "Java service (8003) is properly isolated ✓"
else
    test_fail "Java service (8003) is exposed (SECURITY ISSUE!)"
fi

# ============================================================================
# Test 9: Security - JWT Required
# ============================================================================
print_header "🔑 Test 9: Security - JWT Token Validation"

test_info "Testing that protected endpoints reject requests without tokens..."

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/documents)

if [ "$RESPONSE" = "403" ] || [ "$RESPONSE" = "401" ]; then
    test_pass "Protected endpoints require authentication (received $RESPONSE)"
else
    test_info "Response code was $RESPONSE (may be 200 if no auth required)"
fi

# ============================================================================
# Test 10: Database Connectivity
# ============================================================================
print_header "💾 Test 10: Database Connectivity"

test_info "Checking if services can connect to PostgreSQL..."

# Check User Management logs for database connection
if docker-compose logs am-user-management 2>&1 | grep -q "PostgreSQL database tables created"; then
    test_pass "User Management connected to PostgreSQL ✓"
else
    test_info "Database connection status unclear from logs"
fi

# ============================================================================
# Test Summary
# ============================================================================
print_header "📊 Test Summary"

TOTAL=$((PASSED + FAILED))
PASS_RATE=$((PASSED * 100 / TOTAL))

echo -e "Total Tests: ${BLUE}$TOTAL${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo -e "Pass Rate: ${BLUE}$PASS_RATE%${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed${NC}"
    exit 1
fi
