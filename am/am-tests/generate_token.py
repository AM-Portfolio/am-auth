import jwt
import datetime
import time

SECRET = "jwt-super-secret-signing-key-change-in-production-must-be-32chars-minimum-xyz"
ALGORITHM = "HS256"

def create_token():
    payload = {
        "sub": "test-user-123",
        "user_id": "test-user-123",
        "email": "test@example.com",
        "roles": ["user", "trade:all"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    print(token)

if __name__ == "__main__":
    create_token()
