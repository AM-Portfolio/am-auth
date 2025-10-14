"""Authentication utilities for API Gateway"""
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import logging

from core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

class CurrentUser:
    """Represents the currently authenticated user"""
    def __init__(self, user_id: str, email: str, roles: List[str], token: str):
        self.user_id = user_id
        self.email = email
        self.roles = roles if roles else []
        self.token = token

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Validate user token and get current user info
    This is called for every API request that requires authentication
    """
    try:
        token = credentials.credentials
        
        # Validate token with auth service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/validate",
                json={"token": token},
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.warning(f"Token validation failed: {response.status_code}")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            data = response.json()
            logger.info(f"User authenticated: {data.get('user_id')}")
            
            # Map scopes to roles (validation endpoint returns 'scopes', not 'roles')
            roles = data.get("roles", data.get("scopes", []))
            logger.info(f"User roles/scopes: {roles}")
            
            return CurrentUser(
                user_id=data.get("user_id"),
                email=data.get("email"),
                roles=roles,
                token=token
            )
            
    except httpx.RequestError as e:
        logger.error(f"Auth service error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def generate_service_token(
    user_token: str,
    service_id: str,
    permissions: List[str]
) -> str:
    """
    Generate service token for internal communication
    Converts user token to service token
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/internal/service-token",
                headers={"Authorization": f"Bearer {user_token}"},
                json={
                    "service_id": service_id,
                    "service_name": "API Gateway",
                    "permissions": permissions
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"Service token generation failed: {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate service token"
                )
            
            return response.json()["access_token"]
            
    except httpx.RequestError as e:
        logger.error(f"Error generating service token: {e}")
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating service token: {e}")
        raise HTTPException(status_code=500, detail=str(e))
