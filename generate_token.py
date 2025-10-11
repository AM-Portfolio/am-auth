#!/usr/bin/env python3
import requests
import sys
import time

# Generate unique email
timestamp = str(int(time.time()))
email = f"testuser{timestamp}@example.com"
phone = f"+1555{timestamp[-7:]}"
password = "TestPass123!"

# Step 1: Register user
print(f"Step 1: Registering user {email}...")
reg_response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={"email": email, "password": password, "phone_number": phone}
)

if reg_response.status_code not in [200, 201]:
    print(f"❌ Registration failed: {reg_response.text}")
    sys.exit(1)

print(f"✅ User registered")

# Step 2: Activate user account
print(f"Step 2: Activating user account...")
activate_response = requests.patch(
    f"http://localhost:8000/api/v1/users/email/{email}/status",
    json={"status": "active", "reason": "Email verification completed"},
    headers={"Content-Type": "application/json"}
)

if activate_response.status_code not in [200, 201]:
    print(f"❌ Activation failed: {activate_response.text}")
    sys.exit(1)

print(f"✅ User activated")

# Step 3: Login
print("Step 3: Logging in...")
login_response = requests.post(
    "http://localhost:8001/api/v1/tokens/oauth",
    data={"grant_type": "password", "username": email, "password": password},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if login_response.status_code == 200:
    access_token = login_response.json()["access_token"]
    print(f"✅ Got access token: {access_token[:50]}...")
    
    # Step 4: Generate service token
    print("Step 4: Generating service token...")
    service_response = requests.post(
        "http://localhost:8001/api/v1/internal/service-token",
        json={"service_id": "test-service", "service_name": "Test", "permissions": ["read:documents", "read:reports"]},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if service_response.status_code == 200:
        response_data = service_response.json()
        print(f"Response: {response_data}")
        
        # Try different possible keys
        if "service_token" in response_data:
            service_token = response_data["service_token"]
        elif "token" in response_data:
            service_token = response_data["token"]
        elif "access_token" in response_data:
            service_token = response_data["access_token"]
        else:
            print(f"❌ Could not find token in response: {response_data}")
            sys.exit(1)
            
        print(f"✅ Got service token!")
        print(f"\n{service_token}")
        
        # Save to file
        with open("/Users/munishm/Documents/AM-Repos/auth-test/token.txt", "w") as f:
            f.write(service_token)
        print(f"\n✅ Token saved to token.txt")
        sys.exit(0)
    else:
        print(f"❌ Service token failed: {service_response.text}")
        sys.exit(1)
else:
    print(f"❌ Login failed: {login_response.text}")
    sys.exit(1)
