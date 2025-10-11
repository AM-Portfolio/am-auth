#!/bin/bash

echo "🔑 Generating Fresh Service Token"
echo "=================================="
echo ""

# Step 1: Register user (ignore if exists)
echo "1. Registering test user..."
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"testuser@example.com","password":"testpass123","phone_number":"+1234567890"}' > /dev/null 2>&1

# Step 2: Login to get user token
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/tokens/oauth \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser@example.com&password=testpass123&grant_type=password')

USER_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])' 2>/dev/null)

if [ -z "$USER_TOKEN" ]; then
    echo "❌ Failed to get user token"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Got user token"

# Step 3: Generate service token
echo "3. Generating service token..."
SERVICE_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/internal/service-token \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"service_id":"test-service","service_name":"Test Service","permissions":["read:documents","read:reports"]}')

SERVICE_TOKEN=$(echo $SERVICE_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)["service_token"])' 2>/dev/null)

if [ -z "$SERVICE_TOKEN" ]; then
    echo "❌ Failed to get service token"
    echo "Response: $SERVICE_RESPONSE"
    exit 1
fi

echo "✅ Got service token"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Fresh Service Token:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$SERVICE_TOKEN"
echo ""
echo "Saving to token.txt..."
echo "$SERVICE_TOKEN" > /Users/munishm/Documents/AM-Repos/auth-test/token.txt
echo "✅ Saved to token.txt"
