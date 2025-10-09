"""Google OAuth authentication service"""
from typing import Dict, Any, Optional
from google.oauth2 import id_token
from google.auth.transport import requests
from shared_infra.config.settings import settings
from app.services.google_mock_service import google_mock_service


class GoogleAuthService:
    """Service for Google OAuth token validation and user management"""
    
    @classmethod
    async def verify_google_token(cls, token: str, use_mock: bool = False) -> Dict[str, Any]:
        """
        Verify a Google ID token and extract user information
        
        Args:
            token: The Google ID token to verify
            use_mock: If True, use mock verification for testing
        
        Returns:
            Dictionary containing user information from the token
        
        Raises:
            ValueError: If token is invalid or verification fails
        """
        try:
            if use_mock or not settings.GOOGLE_CLIENT_ID:
                return cls._verify_mock_token(token)
            else:
                return cls._verify_real_google_token(token)
        
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")
    
    @classmethod
    def _verify_mock_token(cls, token: str) -> Dict[str, Any]:
        """Verify a mock Google token for testing"""
        try:
            client_id = google_mock_service.TEST_GOOGLE_CLIENT_ID
            
            if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_ID != client_id:
                client_id = settings.GOOGLE_CLIENT_ID
            
            id_info = google_mock_service.verify_mock_token(token, client_id)
            
            return {
                "sub": id_info["sub"],
                "email": id_info["email"],
                "email_verified": id_info.get("email_verified", True),
                "name": id_info.get("name", ""),
                "given_name": id_info.get("given_name", ""),
                "family_name": id_info.get("family_name", ""),
                "picture": id_info.get("picture", ""),
                "locale": id_info.get("locale", "en"),
                "hd": id_info.get("hd", ""),
                "iss": id_info.get("iss", "https://accounts.google.com"),
                "aud": id_info.get("aud", client_id)
            }
        
        except Exception as e:
            raise ValueError(f"Mock token verification failed: {str(e)}")
    
    @classmethod
    def _verify_real_google_token(cls, token: str) -> Dict[str, Any]:
        """Verify a real Google ID token using Google's public keys"""
        try:
            request = requests.Request()
            
            allowed_client_ids = [settings.GOOGLE_CLIENT_ID]
            
            id_info = id_token.verify_oauth2_token(
                token,
                request,
                settings.GOOGLE_CLIENT_ID
            )
            
            if id_info["aud"] not in allowed_client_ids:
                raise ValueError(f"Token audience not in allowed clients")
            
            if id_info["iss"] not in ["https://accounts.google.com", "accounts.google.com"]:
                raise ValueError(f"Invalid token issuer: {id_info['iss']}")
            
            if settings.google_allowed_domains_list:
                user_domain = id_info.get("hd", "")
                if not user_domain or user_domain not in settings.google_allowed_domains_list:
                    raise ValueError(f"Email domain '{user_domain}' not allowed")
            
            return id_info
        
        except Exception as e:
            raise ValueError(f"Real Google token verification failed: {str(e)}")
    
    @classmethod
    def extract_user_profile(cls, id_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract user profile information from verified Google token
        
        Args:
            id_info: Verified token information from Google
        
        Returns:
            Dictionary with standardized user profile data
        """
        return {
            "google_id": id_info["sub"],
            "email": id_info["email"],
            "email_verified": id_info.get("email_verified", False),
            "name": id_info.get("name", ""),
            "given_name": id_info.get("given_name", ""),
            "family_name": id_info.get("family_name", ""),
            "picture": id_info.get("picture", ""),
            "locale": id_info.get("locale", "en"),
            "hosted_domain": id_info.get("hd", "")
        }


google_auth_service = GoogleAuthService()
