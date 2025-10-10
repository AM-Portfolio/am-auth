"""Mock Google OAuth token generator for testing"""
import time
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt
from shared_infra.config.settings import settings


class GoogleMockService:
    """Generate mock Google ID tokens for testing without real Google OAuth"""
    
    TEST_GOOGLE_CLIENT_ID = "test-google-client-id.apps.googleusercontent.com"
    TEST_PRIVATE_KEY = "test-mock-private-key-for-google-tokens"
    
    @classmethod
    def generate_mock_google_token(
        cls,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None,
        exp_seconds: int = 3600,
        aud: Optional[str] = None,
        sub: Optional[str] = None
    ) -> str:
        """
        Generate a mock Google ID token for testing
        
        Args:
            email: User email address
            name: User's full name
            picture: URL to profile picture
            exp_seconds: Token expiry in seconds (default 1 hour)
            aud: Audience (client ID), uses test client ID if not provided
            sub: Google user ID, generates from email if not provided
        
        Returns:
            Mock Google ID token (JWT)
        """
        now = int(time.time())
        
        if sub is None:
            sub = f"google_user_{hash(email) % 10000000000}"
        
        payload = {
            "iss": "https://accounts.google.com",
            "azp": aud or cls.TEST_GOOGLE_CLIENT_ID,
            "aud": aud or cls.TEST_GOOGLE_CLIENT_ID,
            "sub": str(sub),
            "email": email,
            "email_verified": True,
            "at_hash": "mock_at_hash",
            "iat": now,
            "exp": now + exp_seconds if exp_seconds > 0 else now - 3600,
        }
        
        if name:
            payload["name"] = name
            name_parts = name.split(" ", 1)
            payload["given_name"] = name_parts[0]
            if len(name_parts) > 1:
                payload["family_name"] = name_parts[1]
        
        if picture:
            payload["picture"] = picture
        else:
            payload["picture"] = f"https://lh3.googleusercontent.com/mock/{hash(email)}"
        
        token = jwt.encode(
            payload,
            cls.TEST_PRIVATE_KEY,
            algorithm="HS256"
        )
        
        return token
    
    @classmethod
    def decode_mock_token(cls, token: str) -> Dict[str, Any]:
        """Decode a mock Google token without verification (for testing)"""
        try:
            payload = jwt.decode(
                token,
                cls.TEST_PRIVATE_KEY,
                algorithms=["HS256"],
                options={"verify_signature": True}
            )
            return payload
        except Exception as e:
            raise ValueError(f"Invalid mock token: {str(e)}")
    
    @classmethod
    def verify_mock_token(cls, token: str, client_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify a mock Google token (simulates Google's verification)
        
        Args:
            token: The mock Google ID token
            client_id: Expected client ID (audience)
        
        Returns:
            Decoded token payload
        
        Raises:
            ValueError: If token is invalid
        """
        try:
            payload = cls.decode_mock_token(token)
            
            expected_aud = client_id or cls.TEST_GOOGLE_CLIENT_ID
            if payload.get("aud") != expected_aud:
                raise ValueError(f"Token audience mismatch. Expected: {expected_aud}, Got: {payload.get('aud')}")
            
            if payload["exp"] < int(time.time()):
                raise ValueError("Token has expired")
            
            if payload["iss"] not in ["https://accounts.google.com", "accounts.google.com"]:
                raise ValueError(f"Invalid issuer: {payload['iss']}")
            
            return payload
            
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")


google_mock_service = GoogleMockService()
