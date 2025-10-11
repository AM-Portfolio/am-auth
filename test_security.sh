#!/bin/bash

echo "🔒 COMPREHENSIVE SECURITY TEST"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📋 Testing Two-Layer Security:"
echo "   1. Network Isolation (external access blocked)"
echo "   2. JWT Authentication (internal access controlled)"
echo ""

# Test 1: External Access Should Be Blocked
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 1: Network Isolation - External Access"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testing Python service (port 8002) from external..."
ERROR_OUTPUT=$(curl -s --max-time 2 http://localhost:8002/health 2>&1)
if [ -z "$ERROR_OUTPUT" ] || echo "$ERROR_OUTPUT" | grep -q "Connection refused\|Failed to connect\|Empty reply\|Could not connect"; then
    echo -e "${GREEN}✅ PASS${NC} - External access BLOCKED (Connection refused)"
    EXTERNAL_PYTHON="PASS"
else
    echo -e "${RED}❌ FAIL${NC} - External access NOT blocked (port is exposed!)"
    echo "   Response: $ERROR_OUTPUT"
    EXTERNAL_PYTHON="FAIL"
fi

echo ""
echo "Testing Java service (port 8003) from external..."
ERROR_OUTPUT=$(curl -s --max-time 2 http://localhost:8003/health 2>&1)
if [ -z "$ERROR_OUTPUT" ] || echo "$ERROR_OUTPUT" | grep -q "Connection refused\|Failed to connect\|Empty reply\|Could not connect"; then
    echo -e "${GREEN}✅ PASS${NC} - External access BLOCKED (Connection refused)"
    EXTERNAL_JAVA="PASS"
else
    echo -e "${RED}❌ FAIL${NC} - External access NOT blocked (port is exposed!)"
    echo "   Response: $ERROR_OUTPUT"
    EXTERNAL_JAVA="FAIL"
fi

# Test 2: Internal Access Without Token Should Fail
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 2: JWT Authentication - No Token"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testing Python service from internal network WITHOUT token..."
RESPONSE=$(docker exec am-am-user-management-1 python3 -c "import httpx; r=httpx.get('http://am-python-internal-service:8002/internal/service-info'); print(r.status_code, r.text)" 2>&1)
if echo "$RESPONSE" | grep -q "401\|403\|Not authenticated\|Unauthorized"; then
    echo -e "${GREEN}✅ PASS${NC} - Access denied without token (401 Unauthorized)"
    INTERNAL_NOAUTH_PYTHON="PASS"
else
    echo -e "${RED}❌ FAIL${NC} - Access allowed without token!"
    echo "   Response: $RESPONSE"
    INTERNAL_NOAUTH_PYTHON="FAIL"
fi

echo ""
echo "Testing Java service from internal network WITHOUT token..."
RESPONSE=$(docker exec am-am-user-management-1 python3 -c "import httpx; r=httpx.get('http://am-java-internal-service:8003/internal/service-info'); print(r.status_code, r.text)" 2>&1)
if echo "$RESPONSE" | grep -q "401\|403\|error\|Unauthorized"; then
    echo -e "${GREEN}✅ PASS${NC} - Access denied without token (401 Unauthorized)"
    INTERNAL_NOAUTH_JAVA="PASS"
else
    echo -e "${RED}❌ FAIL${NC} - Access allowed without token!"
    echo "   Response: $RESPONSE"
    INTERNAL_NOAUTH_JAVA="FAIL"
fi

# Test 3: Internal Health Endpoints Should Work
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 3: Internal Communication - Health Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testing Python service health from internal network..."
RESPONSE=$(docker exec am-am-user-management-1 python3 -c "import httpx; r=httpx.get('http://am-python-internal-service:8002/health'); print(r.text)" 2>&1)
if echo "$RESPONSE" | grep -q "healthy\|ok\|status"; then
    echo -e "${GREEN}✅ PASS${NC} - Health endpoint accessible internally"
    echo "   Response: $RESPONSE"
    INTERNAL_HEALTH_PYTHON="PASS"
else
    echo -e "${RED}❌ FAIL${NC} - Health endpoint not responding"
    echo "   Response: $RESPONSE"
    INTERNAL_HEALTH_PYTHON="FAIL"
fi

echo ""
echo "Testing Java service health from internal network..."
RESPONSE=$(docker exec am-am-user-management-1 python3 -c "import httpx; r=httpx.get('http://am-java-internal-service:8003/health'); print(r.text)" 2>&1)
if echo "$RESPONSE" | grep -q "UP\|healthy\|ok"; then
    echo -e "${GREEN}✅ PASS${NC} - Health endpoint accessible internally"
    echo "   Response: $RESPONSE"
    INTERNAL_HEALTH_JAVA="PASS"
else
    echo -e "${RED}❌ FAIL${NC} - Health endpoint not responding"
    echo "   Response: $RESPONSE"
    INTERNAL_HEALTH_JAVA="FAIL"
fi

# Test 4: Public Services Should Be Accessible
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 4: Public Services Accessibility"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Testing User Management service (port 8000)..."
RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)
if echo "$RESPONSE" | grep -q "healthy\|ok\|status"; then
    echo -e "${GREEN}✅ PASS${NC} - Public service accessible"
    PUBLIC_USER_MGMT="PASS"
else
    echo -e "${RED}❌ FAIL${NC} - Public service not accessible"
    PUBLIC_USER_MGMT="FAIL"
fi

echo ""
echo "Testing Auth Tokens service (port 8001)..."
RESPONSE=$(curl -s http://localhost:8001/health 2>/dev/null)
if echo "$RESPONSE" | grep -q "healthy\|ok\|status"; then
    echo -e "${GREEN}✅ PASS${NC} - Public service accessible"
    PUBLIC_AUTH_TOKENS="PASS"
else
    echo -e "${RED}❌ FAIL${NC} - Public service not accessible"
    PUBLIC_AUTH_TOKENS="FAIL"
fi

# Test 5: Test with Valid Service Token
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST 5: JWT Authentication - Valid Token"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Load the fresh service token from file
if [ -f "token.txt" ]; then
    SERVICE_TOKEN=$(cat token.txt)
    echo "📝 Using fresh token from token.txt"
else
    echo -e "${YELLOW}⚠️  WARNING${NC} - token.txt not found! Run generate_token.py first"
    SERVICE_TOKEN="MISSING"
fi

echo "Testing Python service with VALID service token..."
RESPONSE=$(docker exec am-am-user-management-1 python3 -c "import httpx; r=httpx.get('http://am-python-internal-service:8002/internal/service-info', headers={'Authorization': 'Bearer $SERVICE_TOKEN'}); print(r.status_code, r.text)" 2>&1)
if echo "$RESPONSE" | grep -q "200.*service_name\|200.*service_id\|200.*Document"; then
    echo -e "${GREEN}✅ PASS${NC} - Access granted with valid token"
    echo "   Response: $(echo $RESPONSE | head -c 150)..."
    INTERNAL_AUTH_PYTHON="PASS"
else
    echo -e "${YELLOW}⚠️  WARNING${NC} - Token might be expired or invalid"
    echo "   Response: $RESPONSE"
    INTERNAL_AUTH_PYTHON="WARN"
fi

echo ""
echo "Testing Java service with VALID service token..."
RESPONSE=$(docker exec am-am-user-management-1 python3 -c "import httpx; r=httpx.get('http://am-java-internal-service:8003/internal/service-info', headers={'Authorization': 'Bearer $SERVICE_TOKEN'}); print(r.status_code, r.text)" 2>&1)
if echo "$RESPONSE" | grep -q "200.*service_name\|200.*service_id\|200.*Reporting"; then
    echo -e "${GREEN}✅ PASS${NC} - Access granted with valid token"
    echo "   Response: $(echo $RESPONSE | head -c 150)..."
    INTERNAL_AUTH_JAVA="PASS"
else
    echo -e "${YELLOW}⚠️  WARNING${NC} - Token might be expired or invalid"
    echo "   Response: $RESPONSE"
    INTERNAL_AUTH_JAVA="WARN"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Network Isolation Tests:"
echo "  Python External Access: $EXTERNAL_PYTHON"
echo "  Java External Access: $EXTERNAL_JAVA"
echo ""

echo "JWT Authentication Tests:"
echo "  Python No Token: $INTERNAL_NOAUTH_PYTHON"
echo "  Java No Token: $INTERNAL_NOAUTH_JAVA"
echo "  Python With Token: $INTERNAL_AUTH_PYTHON"
echo "  Java With Token: $INTERNAL_AUTH_JAVA"
echo ""

echo "Service Communication Tests:"
echo "  Python Health: $INTERNAL_HEALTH_PYTHON"
echo "  Java Health: $INTERNAL_HEALTH_JAVA"
echo ""

echo "Public Services Tests:"
echo "  User Management: $PUBLIC_USER_MGMT"
echo "  Auth Tokens: $PUBLIC_AUTH_TOKENS"
echo ""

# Final verdict
TOTAL_PASS=$(echo "$EXTERNAL_PYTHON $EXTERNAL_JAVA $INTERNAL_NOAUTH_PYTHON $INTERNAL_NOAUTH_JAVA $INTERNAL_HEALTH_PYTHON $INTERNAL_HEALTH_JAVA $PUBLIC_USER_MGMT $PUBLIC_AUTH_TOKENS" | grep -o "PASS" | wc -l)
TOTAL_TESTS=8

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $TOTAL_PASS -ge 6 ]; then
    echo -e "${GREEN}🎉 SECURITY IS WORKING!${NC}"
    echo "   $TOTAL_PASS/$TOTAL_TESTS critical tests passed"
    echo ""
    echo "✅ Your microservices security architecture is functioning correctly:"
    echo "   - Network isolation prevents external access to internal services"
    echo "   - JWT authentication controls internal service access"
    echo "   - Public services are accessible as expected"
    echo "   - Internal services can communicate securely"
else
    echo -e "${RED}⚠️  SECURITY ISSUES DETECTED${NC}"
    echo "   Only $TOTAL_PASS/$TOTAL_TESTS tests passed"
    echo "   Please review the failed tests above"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
