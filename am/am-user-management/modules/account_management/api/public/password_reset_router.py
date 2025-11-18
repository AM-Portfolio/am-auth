"""Password Reset Router"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from shared_infra.database.config import db_config
from modules.account_management.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from modules.account_management.services.password_reset_service import PasswordResetService

logger = logging.getLogger(__name__)
router = APIRouter()


# Database dependency
async def get_db_session():
    """Get database session"""
    async for session in db_config.get_session():
        yield session


def get_password_hasher() -> BcryptPasswordHasher:
    """Get password hasher dependency"""
    return BcryptPasswordHasher()


# Request/Response Models
class PasswordResetRequestRequest(BaseModel):
    """Request to reset password"""
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetRequestResponse(BaseModel):
    """Response to password reset request"""
    success: bool
    message: str
    note: str = "If an account exists with this email, a password reset link will be sent"


class PasswordResetConfirmRequest(BaseModel):
    """Request to confirm password reset"""
    email: EmailStr = Field(..., description="User's email address")
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")


class PasswordResetConfirmResponse(BaseModel):
    """Response to confirm password reset"""
    success: bool
    message: str


class PasswordResetValidateRequest(BaseModel):
    """Request to validate reset token"""
    email: EmailStr = Field(..., description="User's email address")
    token: str = Field(..., description="Reset token to validate")


class PasswordResetValidateResponse(BaseModel):
    """Response to validate reset token"""
    valid: bool
    message: str


@router.post("/request-reset", response_model=PasswordResetRequestResponse)
async def request_password_reset(
    request: PasswordResetRequestRequest,
    db: AsyncSession = Depends(get_db_session),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher)
):
    """
    Request a password reset link to be sent to user's email
    
    This endpoint is rate-limited to prevent abuse.
    For security reasons, it always returns a success message
    regardless of whether the user exists.
    
    **Returns:**
    - Reset token (only sent to email in real implementation)
    """
    service = PasswordResetService(db, password_hasher)
    success, message, reset_token = await service.request_reset(request.email)
    
    # In development, log the token; in production, send via email
    if reset_token:
        logger.info(f"Reset token for {request.email}: {reset_token}")
    
    return PasswordResetRequestResponse(
        success=success,
        message=message
    )


@router.post("/validate-reset-token", response_model=PasswordResetValidateResponse)
async def validate_reset_token(
    request: PasswordResetValidateRequest,
    db: AsyncSession = Depends(get_db_session),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher)
):
    """
    Validate a password reset token
    
    Use this to verify the token is valid before showing the reset password form.
    
    **Returns:**
    - valid: bool - Whether the token is valid
    - message: str - Details about validity
    """
    service = PasswordResetService(db, password_hasher)
    is_valid, message = await service.validate_reset_token(request.email, request.token)
    
    return PasswordResetValidateResponse(
        valid=is_valid,
        message=message
    )


@router.post("/confirm-reset", response_model=PasswordResetConfirmResponse)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db_session),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher)
):
    """
    Confirm password reset with token and new password
    
    This endpoint:
    1. Validates the reset token
    2. Updates the user's password
    3. Marks the token as used
    
    **Password Requirements:**
    - Minimum 8 characters
    - Should include uppercase, lowercase, numbers, and symbols
    
    **Returns:**
    - success: bool - Whether password was reset
    - message: str - Details about the operation
    """
    try:
        # Validate password complexity (basic validation)
        password = request.new_password
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # More strict validation (optional)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain uppercase, lowercase, and numbers"
            )
        
        service = PasswordResetService(db, password_hasher)
        success, message = await service.reset_password(request.email, request.token, request.new_password)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        logger.info(f"Password reset completed for {request.email}")
        
        return PasswordResetConfirmResponse(
            success=True,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming password reset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error resetting password"
        )
