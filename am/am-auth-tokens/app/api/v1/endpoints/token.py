from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import httpx
import os
import time
from app.core.security import create_access_token, Token
from app.services.user_validation import (
    UserValidationService, 
    UserCredentials,
    user_validation_service
)
from app.api.v1.deps import get_user_validation_service
from shared_infra.config.settings import settings

# Import logging
import sys
from pathlib import Path
shared_path = Path(__file__).parent.parent.parent.parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))
from shared.logging import get_logger

logger = get_logger("am-auth-tokens.token")

router = APIRouter()


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenByUserIdRequest(BaseModel):
    user_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    username: str
    email: str


class ServiceTokenRequest(BaseModel):
    service_id: str
    consumer_key: str
    consumer_secret: str


class ServiceTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    service_id: str
    scopes: list


@router.post("/tokens", response_model=TokenResponse)
async def create_token(
    token_request: TokenRequest,
    user_service: UserValidationService = Depends(get_user_validation_service)
):
    """
    Create a new access token for valid user credentials.
    
    Args:
        token_request: User credentials for token creation
        user_service: User validation service dependency
    
    Returns:
        TokenResponse with access token and user information
    
    Raises:
        HTTPException: If credentials are invalid
    """
    start_time = time.time()
    logger.info(f"🔐 Token creation request received", extra={
        "username": token_request.username,
        "endpoint": "/tokens",
        "method": "POST"
    })
    
    # Validate user credentials
    logger.debug(f"Validating credentials for user: {token_request.username}", extra={
        "username": token_request.username,
        "step": "credential_validation"
    })
    
    credentials = UserCredentials(
        username=token_request.username,
        password=token_request.password
    )
    
    validation_start = time.time()
    validation_result = await user_service.validate_user_credentials(credentials)
    validation_duration = (time.time() - validation_start) * 1000
    
    logger.info(f"User validation completed", extra={
        "username": token_request.username,
        "valid": validation_result.valid,
        "duration_ms": round(validation_duration, 2),
        "step": "validation_complete"
    })
    
    if not validation_result.valid:
        logger.warning(f"❌ Authentication failed for user: {token_request.username}", extra={
            "username": token_request.username,
            "reason": validation_result.message,
            "status_code": 401
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=validation_result.message or "Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user account is active before issuing token
    # Treat missing status as security failure - reject if status is absent or not ACTIVE
    if not validation_result.status or validation_result.status.upper() != "ACTIVE":
        status_msg = validation_result.status if validation_result.status else "unknown"
        logger.warning(f"⛔ User account not active: {token_request.username}", extra={
            "username": token_request.username,
            "user_id": validation_result.user_id,
            "status": status_msg,
            "status_code": 403
        })
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is not active: {status_msg}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token with user data
    logger.debug(f"Creating JWT token for user: {validation_result.username}", extra={
        "user_id": validation_result.user_id,
        "username": validation_result.username,
        "email": validation_result.email,
        "scopes": validation_result.scopes,
        "step": "token_creation"
    })
    
    user_data = {
        "username": validation_result.username,
        "email": validation_result.email,
        "scopes": validation_result.scopes
    }
    
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    token_start = time.time()
    access_token = create_access_token(
        subject=validation_result.user_id,
        user_data=user_data,
        expires_delta=access_token_expires
    )
    token_duration = (time.time() - token_start) * 1000
    
    total_duration = (time.time() - start_time) * 1000
    logger.info(f"✅ Token created successfully for user: {validation_result.username}", extra={
        "user_id": validation_result.user_id,
        "username": validation_result.username,
        "email": validation_result.email,
        "expires_in_minutes": settings.JWT_EXPIRE_MINUTES,
        "token_creation_ms": round(token_duration, 2),
        "total_duration_ms": round(total_duration, 2),
        "status_code": 200
    })
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,  # Convert to seconds
        user_id=validation_result.user_id,
        username=validation_result.username,
        email=validation_result.email
    )


@router.post("/tokens/by-user-id", response_model=TokenResponse)
async def create_token_by_user_id(
    request: TokenByUserIdRequest,
    user_service: UserValidationService = Depends(get_user_validation_service)
):
    """
    Create a new access token for a validated user ID.
    This endpoint matches the sequence diagram where the client already has a user_id
    from the am-user-management service login.
    
    Args:
        request: Request containing user_id
        user_service: User validation service dependency
    
    Returns:
        TokenResponse with access token and user information
    
    Raises:
        HTTPException: If user is not found or inactive
    """
    # Get user information by ID
    user_data = await user_service.get_user_by_id(request.user_id)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is active
    if user_data.get("status") != "ACTIVE" and user_data.get("active") != True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    # Create token with user data
    token_user_data = {
        "username": user_data.get("username", user_data.get("email")),
        "email": user_data.get("email"),
        "scopes": user_data.get("scopes", ["read"])
    }
    
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=request.user_id,
        user_data=token_user_data,
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,  # Convert to seconds
        user_id=request.user_id,
        username=token_user_data["username"],
        email=token_user_data["email"]
    )


@router.post("/tokens/oauth", response_model=TokenResponse)
async def create_token_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserValidationService = Depends(get_user_validation_service)
):
    """
    OAuth2 compatible token endpoint.
    This endpoint validates credentials directly with User Management service
    without creating a circular dependency.
    
    Args:
        form_data: OAuth2 password form data
        user_service: User validation service dependency
    
    Returns:
        TokenResponse with access token and user information
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Validate credentials directly with User Management's internal validate endpoint
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.USER_SERVICE_URL}/internal/v1/auth/validate-credentials",
                json={
                    "email": form_data.username,
                    "password": form_data.password
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="User service error",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user_data_response = response.json()
            
            # Check if user account is active
            if user_data_response.get("status", "").upper() != "ACTIVE":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User account is not active: {user_data_response.get('status', 'unknown')}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create token with user data
            user_data = {
                "username": user_data_response.get("username", user_data_response.get("email")),
                "email": user_data_response.get("email"),
                "scopes": user_data_response.get("scopes", ["read"])
            }
            
            access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
            access_token = create_access_token(
                subject=user_data_response["user_id"],
                user_data=user_data,
                expires_delta=access_token_expires
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.JWT_EXPIRE_MINUTES * 60,
                user_id=user_data_response["user_id"],
                username=user_data["username"],
                email=user_data_response["email"]
            )
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"User service unavailable: {str(e)}"
        )

@router.post("/tokens/service", response_model=ServiceTokenResponse)
async def create_service_token(
    token_request: ServiceTokenRequest
):
    """
    Create a new access token for registered service/application.
    
    Args:
        token_request: Service credentials (service_id, consumer_key, consumer_secret)
    
    Returns:
        ServiceTokenResponse with access token and service information
    
    Raises:
        HTTPException: If service credentials are invalid
    """
    # Call User Management service to validate service credentials
    user_service_url = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{user_service_url}/api/v1/service/validate-credentials",
                json={
                    "consumer_key": token_request.consumer_key,
                    "consumer_secret": token_request.consumer_secret
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid service credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            validation_data = response.json()
            
            if not validation_data.get("valid"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=validation_data.get("message", "Invalid service credentials"),
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify service_id matches
            if validation_data.get("service_id") != token_request.service_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Service ID mismatch",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Create token with service data
            service_data = {
                "service_id": validation_data.get("service_id"),
                "scopes": validation_data.get("scopes", []),
                "type": "service"
            }
            
            access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
            access_token = create_access_token(
                subject=validation_data.get("service_id"),
                user_data=service_data,
                expires_delta=access_token_expires
            )
            
            return ServiceTokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.JWT_EXPIRE_MINUTES * 60,  # Convert to seconds
                service_id=validation_data.get("service_id"),
                scopes=validation_data.get("scopes", [])
            )
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"User Management service unavailable: {str(e)}"
        )
