"""
Internal service token management endpoints
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import jwt

# Import shared auth utilities if available
try:
    import sys
    from pathlib import Path
    shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
    if str(shared_path) not in sys.path:
        sys.path.insert(0, str(shared_path))
    
    from shared.auth.jwt_utils import jwt_validator
    from shared.logging import get_logger
    logger = get_logger("am-auth-tokens.internal")
except ImportError:
    import logging
    logger = logging.getLogger("am-auth-tokens.internal")

router = APIRouter()

# Configuration
INTERNAL_JWT_SECRET = os.getenv("INTERNAL_JWT_SECRET", "internal-service-super-secret-key-32chars-minimum-change-in-prod")
SERVICE_TOKEN_EXPIRY_MINUTES = int(os.getenv("SERVICE_TO_SERVICE_TOKEN_EXPIRY_MINUTES", "60"))

# Models
class ServiceTokenRequest(BaseModel):
    service_id: str
    service_name: str
    permissions: Optional[List[str]] = []
    expiry_minutes: Optional[int] = SERVICE_TOKEN_EXPIRY_MINUTES

class ServiceTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    service_id: str
    permissions: List[str]

class TokenIntrospectRequest(BaseModel):
    token: str

class TokenIntrospectResponse(BaseModel):
    active: bool
    service_id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    token_type: Optional[str] = None
    permissions: Optional[List[str]] = []
    exp: Optional[int] = None
    iat: Optional[int] = None

# Predefined service permissions
SERVICE_PERMISSIONS = {
    "am-python-internal-service": [
        "read:documents", "write:documents", "process:documents"
    ],
    "am-java-internal-service": [
        "read:reports", "write:reports", "generate:reports"
    ],
    "am-user-management": [
        "read:users", "write:users", "manage:users"
    ]
}

@router.post("/service-token", response_model=ServiceTokenResponse)
async def generate_service_token(request: ServiceTokenRequest):
    """Generate a service-to-service authentication token"""
    try:
        # Validate service ID
        if not request.service_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service ID is required"
            )
        
        # Get default permissions for known services
        default_permissions = SERVICE_PERMISSIONS.get(request.service_id, [])
        permissions = request.permissions if request.permissions else default_permissions
        
        # Generate token
        now = datetime.utcnow()
        payload = {
            "service_id": request.service_id,
            "sub": request.service_id,
            "service_name": request.service_name,
            "username": request.service_name,
            "type": "service_token",
            "roles": permissions,
            "permissions": permissions,
            "scope": " ".join(permissions),
            "exp": now + timedelta(minutes=request.expiry_minutes),
            "iat": now,
            "iss": "am-auth-tokens"
        }
        
        token = jwt.encode(payload, INTERNAL_JWT_SECRET, algorithm="HS256")
        
        logger.info(f"Generated service token for {request.service_id}", extra={
            "service_id": request.service_id,
            "permissions": permissions,
            "expiry_minutes": request.expiry_minutes
        })
        
        return ServiceTokenResponse(
            access_token=token,
            expires_in=request.expiry_minutes * 60,  # Convert to seconds
            service_id=request.service_id,
            permissions=permissions
        )
        
    except Exception as e:
        logger.error(f"Failed to generate service token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate service token"
        )

@router.post("/introspect", response_model=TokenIntrospectResponse)
async def introspect_token(request: TokenIntrospectRequest):
    """Introspect a token to get its details and validity"""
    try:
        user_jwt_secret = os.getenv("JWT_SECRET", "your-secret-key-here-change-in-production")
        
        # Try to decode as user token first
        try:
            payload = jwt.decode(request.token, user_jwt_secret, algorithms=["HS256"])
            if payload.get("type") == "user_token":
                return TokenIntrospectResponse(
                    active=True,
                    user_id=payload.get("user_id"),
                    username=payload.get("username"),
                    token_type="user",
                    exp=payload.get("exp"),
                    iat=payload.get("iat")
                )
        except jwt.JWTError:
            pass
        
        # Try to decode as service token
        try:
            payload = jwt.decode(request.token, INTERNAL_JWT_SECRET, algorithms=["HS256"])
            if payload.get("type") == "service_token":
                return TokenIntrospectResponse(
                    active=True,
                    service_id=payload.get("service_id"),
                    token_type="service",
                    permissions=payload.get("permissions", []),
                    exp=payload.get("exp"),
                    iat=payload.get("iat")
                )
        except jwt.JWTError:
            pass
        
        # Token is invalid
        return TokenIntrospectResponse(active=False)
        
    except Exception as e:
        logger.error(f"Token introspection failed: {str(e)}")
        return TokenIntrospectResponse(active=False)

@router.get("/service-permissions/{service_id}")
async def get_service_permissions(service_id: str):
    """Get default permissions for a service"""
    permissions = SERVICE_PERMISSIONS.get(service_id, [])
    
    return {
        "service_id": service_id,
        "default_permissions": permissions,
        "available_permissions": [
            "read:documents", "write:documents", "process:documents",
            "read:reports", "write:reports", "generate:reports", 
            "read:users", "write:users", "manage:users"
        ]
    }

@router.get("/services")
async def list_registered_services():
    """List all registered services and their default permissions"""
    return {
        "services": [
            {
                "service_id": service_id,
                "default_permissions": permissions
            }
            for service_id, permissions in SERVICE_PERMISSIONS.items()
        ]
    }