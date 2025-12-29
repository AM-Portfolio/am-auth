"""Test endpoints for Google OAuth without requiring real Google integration"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from app.services.google_mock_service import google_mock_service


router = APIRouter()


class MockGoogleTokenRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    exp: Optional[int] = 3600


class MockGoogleTokenResponse(BaseModel):
    id_token: str
    expires_in: int
    token_type: str = "Bearer"
    email: str
    token_info: Dict[str, Any]


class GoogleAuthSetupResponse(BaseModel):
    status: str
    test_client_id: str
    message: str
    test_scenarios: List[str]


@router.post("/mock/google/token", response_model=MockGoogleTokenResponse)
async def generate_mock_google_token(request: MockGoogleTokenRequest):
    """
    Generate a mock Google ID token for testing
    
    This endpoint creates a fake Google ID token that can be used to test
    the Google authentication flow without requiring real Google OAuth setup.
    """
    try:
        id_token = google_mock_service.generate_mock_google_token(
            email=request.email,
            name=request.name,
            picture=request.picture,
            exp_seconds=request.exp
        )
        
        try:
            token_info = google_mock_service.decode_mock_token(id_token)
        except:
            token_info = {"email": request.email, "name": request.name}
        
        return MockGoogleTokenResponse(
            id_token=id_token,
            expires_in=request.exp,
            email=request.email,
            token_info=token_info
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate mock token: {str(e)}"
        )


@router.post("/setup/google-auth", response_model=GoogleAuthSetupResponse)
async def setup_google_auth_testing():
    """
    Setup Google auth testing environment
    
    Returns configuration and information needed for testing Google OAuth
    without requiring real Google credentials.
    """
    return GoogleAuthSetupResponse(
        status="ready",
        test_client_id=google_mock_service.TEST_GOOGLE_CLIENT_ID,
        message="Google auth test environment is ready. Use /test/mock/google/token to generate test tokens.",
        test_scenarios=[
            "new_user_registration",
            "existing_user_login",
            "invalid_token_handling",
            "expired_token_handling",
            "email_domain_validation"
        ]
    )


@router.get("/info/google-auth")
async def get_google_auth_info():
    """
    Get information about Google auth testing setup
    """
    return {
        "test_client_id": google_mock_service.TEST_GOOGLE_CLIENT_ID,
        "endpoints": {
            "generate_mock_token": "POST /test/mock/google/token",
            "setup_environment": "POST /test/setup/google-auth",
            "authenticate": "POST /api/v1/auth/google/token",
            "validate": "POST /api/v1/validate"
        },
        "example_request": {
            "email": "testuser@gmail.com",
            "name": "Test User",
            "picture": "https://lh3.googleusercontent.com/test",
            "exp": 3600
        },
        "notes": [
            "Mock tokens are for testing only",
            "Use test_client_id for token audience validation",
            "Tokens expire based on the 'exp' parameter (default: 1 hour)"
        ]
    }
