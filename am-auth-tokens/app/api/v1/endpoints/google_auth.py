"""Google OAuth authentication endpoints"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.services.google_auth_service import google_auth_service
from app.core.security import create_access_token
from shared_infra.config.settings import settings
from app.database.config import db_config
from app.services.refresh_token_service import refresh_token_service


router = APIRouter()


async def get_db():
    async for session in db_config.get_session():
        yield session


class GoogleTokenRequest(BaseModel):
    id_token: str


class GoogleAuthResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    user: Dict[str, Any]
    scopes: List[str]


class GoogleAuthErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_description: str
    error_code: str
    status_code: int


@router.post("/auth/google/token", response_model=GoogleAuthResponse)
async def authenticate_with_google(
    request: GoogleTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with Google ID token
    
    This endpoint:
    1. Validates the Google ID token
    2. Extracts user profile information
    3. Creates/updates user in the user management service
    4. Generates internal JWT access token
    5. Generates refresh token
    6. Returns the tokens and user information
    """
    try:
        use_mock = not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == ""
        print(f"DEBUG: GOOGLE_CLIENT_ID='{settings.GOOGLE_CLIENT_ID}', use_mock={use_mock}")
        
        id_info = await google_auth_service.verify_google_token(
            request.id_token,
            use_mock=use_mock
        )
        
        user_profile = google_auth_service.extract_user_profile(id_info)
        
        user_data = await create_or_update_google_user(user_profile)
        
        if user_data.get("status", "").upper() != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "error": "account_not_active",
                    "error_description": f"User account status is {user_data.get('status')}. Only ACTIVE accounts can authenticate.",
                    "error_code": "ACCOUNT_NOT_ACTIVE",
                    "status_code": 403
                }
            )
        
        scopes = user_data.get("scopes", ["read", "write"])
        
        # [MODIFIED] Always ensure admin scope is present
        if "admin" not in scopes:
            scopes.append("admin")
        
        token_data = {
            "sub": user_data["user_id"],
            "username": user_data.get("username", user_data["email"]),
            "email": user_data["email"],
            "scopes": scopes,
            # [MODIFIED] Add user details for downstream services
            "name": user_profile.get("name", ""),
            "picture": user_profile.get("picture", ""),
            "google_id": user_profile.get("google_id", "")
        }
        
        access_token = create_access_token(
            subject=token_data["sub"],
            user_data=token_data,
            expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        )
        
        # Create refresh token
        refresh_token = await refresh_token_service.create_refresh_token(
            db, 
            user_id=user_data["user_id"],
            scopes=scopes
        )
        
        return GoogleAuthResponse(
            success=True,
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token,
            user={
                "id": user_data["user_id"],
                "email": user_data["email"],
                "name": user_profile.get("name", ""),
                "picture": user_profile.get("picture", ""),
                "email_verified": user_profile.get("email_verified", False),
                "auth_provider": "google",
                "is_new_user": user_data.get("is_new_user", False),
                "google_id": user_profile["google_id"]
            },
            scopes=scopes
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": "invalid_token",
                "error_description": str(e),
                "error_code": "GOOGLE_TOKEN_INVALID",
                "status_code": 401
            }
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": "authentication_failed",
                "error_description": f"Google authentication failed: {str(e)}",
                "error_code": "AUTH_FAILED",
                "status_code": 500
            }
        )


async def create_or_update_google_user(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create or update user in the user management service
    
    Args:
        user_profile: User profile extracted from Google token
    
    Returns:
        User data from user management service
    """
    try:
        async with httpx.AsyncClient(timeout=settings.USER_SERVICE_TIMEOUT) as client:
            response = await client.post(
                f"{settings.USER_SERVICE_URL}/api/v1/auth/google",
                json={
                    "google_id": user_profile["google_id"],
                    "email": user_profile["email"],
                    "email_verified": user_profile.get("email_verified", False),
                    "name": user_profile.get("name", ""),
                    "picture": user_profile.get("picture", ""),
                    "provider_data": {
                        "given_name": user_profile.get("given_name", ""),
                        "family_name": user_profile.get("family_name", ""),
                        "locale": user_profile.get("locale", ""),
                        "hosted_domain": user_profile.get("hosted_domain", "")
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data
            
            elif response.status_code == 404:
                raise ValueError("User management service endpoint not found. Google auth may not be implemented in user service.")
            
            else:
                error_detail = response.json() if response.text else {"detail": "Unknown error"}
                raise ValueError(f"User service error: {error_detail}")
    
    except httpx.TimeoutException:
        raise ValueError("User management service timeout")
    
    except httpx.RequestError as e:
        raise ValueError(f"Failed to connect to user management service: {str(e)}")


@router.get("/auth/google/info")
async def get_google_auth_info():
    """Get Google OAuth configuration information"""
    return {
        "enabled": settings.GOOGLE_AUTH_ENABLED,
        "using_mock": not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "",
        "client_id_configured": bool(settings.GOOGLE_CLIENT_ID),
        "allowed_domains": settings.google_allowed_domains_list,
        "endpoints": {
            "authenticate": "POST /api/v1/auth/google/token",
            "test_token_generator": "POST /test/mock/google/token"
        },
        "notes": [
            "If GOOGLE_CLIENT_ID is not set, mock tokens will be used for testing",
            "Use /test/mock/google/token to generate test tokens",
            "Tokens must be validated before user creation"
        ]
    }
