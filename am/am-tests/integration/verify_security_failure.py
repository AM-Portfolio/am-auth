import requests
import jwt
import datetime
import sys

# Configuration
API_GATEWAY_URL = "http://localhost:8000"
# WRONG SECRET - This simulates a hacker trying to forge a token
FAKE_SECRET = "this-is-not-the-correct-secret-key-at-all" 
JWT_ALGORITHM = "HS256"

def generate_fake_token():
    """Generate a FORGED token signed with the WRONG secret"""
    payload = {
        "user_id": "hacker-123",
        "email": "hacker@example.com",
        "roles": ["admin"], 
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    # Sign with the WRONG secret
    token = jwt.encode(payload, FAKE_SECRET, algorithm=JWT_ALGORITHM)
    return token

def test_security_rejection():
    print("--- Security Verification: Negative Test ---")
    print("Goal: Prove that the Trade Service REJECTS invalid tokens.")
    
    token = generate_fake_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_GATEWAY_URL}/api/v1/trades"
    
    print(f"Target: {url}")
    print("Sending request with FORGED token...")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Service returned 401 Unauthorized.")
            print("   This proves the Security Layer CHECKED the signature and REJECTED it.")
        elif response.status_code == 500:
            print("❌ FAILURE: Service returned 500.")
            print("   This means it ACCEPTED the fake token and tried to process it.")
            print("   Security is NOT working!")
        else:
            print(f"⚠️ UNEXPECTED: Service returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_security_rejection()
