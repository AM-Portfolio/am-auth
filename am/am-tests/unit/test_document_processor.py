import requests
import jwt
import datetime
import os
import sys

# Configuration
API_GATEWAY_URL = "http://localhost:8000"
JWT_SECRET = "jwt-super-secret-signing-key-change-in-production-must-be-32chars-minimum-xyz"
JWT_ALGORITHM = "HS256"

def generate_test_token():
    """Generate a valid user token for testing"""
    payload = {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "roles": ["user", "admin"], # Admin needed for some endpoints
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def test_document_types():
    """Test the public endpoint /documents/types"""
    token = generate_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # The Gateway proxy maps /api/v1/documents/{path} -> Document Processor
    # But wait, looking at document_processor.py:
    # @router.api_route("/documents/{path:path}")
    # So it's /api/v1/documents/types -> /api/v1/documents/types
    
    url = f"{API_GATEWAY_URL}/api/v1/documents/types"
    print(f"Testing URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Document Processor accepted the request (Token validated)")
        else:
            print("❌ FAILED: Document Processor rejected the request")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_document_types()
