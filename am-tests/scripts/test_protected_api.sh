#!/bin/bash
echo "Generating mock token..."
RESPONSE=$(curl -s -X POST http://localhost:8002/test/mock/google/token -H "Content-Type: application/json" -d '{"email": "test@example.com", "name": "Test User"}')
ID_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id_token', ''))")

if [ -z "$ID_TOKEN" ]; then
  echo "Failed to get ID token"
  exit 1
fi

echo "Exchanging token for Access Token..."
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8002/api/v1/auth/google/token -H "Content-Type: application/json" -d "{\"id_token\": \"$ID_TOKEN\"}")
ACCESS_TOKEN=$(echo $AUTH_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to get Access Token"
  echo "Response: $AUTH_RESPONSE"
  exit 1
fi

echo "Access Token: $ACCESS_TOKEN"

echo "Testing Protected API (Document Types)..."
curl -v -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/api/v1/documents/types
