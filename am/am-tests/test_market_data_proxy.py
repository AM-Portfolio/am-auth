import jwt
import datetime
import requests
import json

# Configuration
SECRET = "jwt-super-secret-signing-key-change-in-production-must-be-32chars-minimum-xyz"
ALGORITHM = "HS256"
API_GATEWAY_URL = "http://localhost:8000"

def create_token():
    payload = {
        "sub": "test-user-123",
        "user_id": "test-user-123",
        "email": "test@example.com",
        "roles": ["user", "trade:all"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token

def test_market_data_proxy():
    token = create_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test brokerage breakeven endpoint (stateless)
    endpoint = "/api/v1/brokerage/breakeven"
    params = {
        "symbol": "RELIANCE",
        "price": "2500",
        "quantity": "10",
        "exchange": "NSE",
        "tradeType": "DELIVERY",
        "brokerType": "DISCOUNT"
    }
    url = f"{API_GATEWAY_URL}{endpoint}"
    
    print(f"Testing endpoint: {url}")
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response Content:")
            try:
                print(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                print(response.text)
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API Gateway. Is it running?")

def generate_service_token_for_debug():
    INTERNAL_SECRET = "internal-service-super-secret-key-32chars-minimum-change-in-prod"
    payload = {
        "sub": "api-gateway",
        "scope": "market-data:read read write openid profile email",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        "iat": datetime.datetime.utcnow(),
        "iss": "am-auth-tokens"
    }
    token = jwt.encode(payload, INTERNAL_SECRET, algorithm=ALGORITHM)
    print(f"\nDebug Service Token:\n{token}\n")
    return token

if __name__ == "__main__":
    test_market_data_proxy()
