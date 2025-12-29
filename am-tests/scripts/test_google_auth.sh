#!/bin/bash
echo "Generating mock token..."
RESPONSE=$(curl -s -X POST http://localhost:8002/test/mock/google/token -H "Content-Type: application/json" -d '{"email": "test@example.com", "name": "Test User"}')
echo "Response: $RESPONSE"

# Simple extraction of id_token using python to avoid grep/sed complexity with json
ID_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id_token', ''))")
echo "ID Token: $ID_TOKEN"

if [ -z "$ID_TOKEN" ]; then
  echo "Failed to get ID token"
  exit 1
fi

echo "Exchanging token..."
curl -s -X POST http://localhost:8002/api/v1/auth/google/token -H "Content-Type: application/json" -d "{\"id_token\": \"$ID_TOKEN\"}"
