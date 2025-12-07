"""
User Status Management Router

Endpoints for checking and updating user account status
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime, timezone

from modules.account_management.infrastructure.models.user_account_orm import UserAccountORM
from modules.account_management.domain.enums.user_status import UserStatus
from shared_infra.database.config import db_config

router = APIRouter()


# Database session dependency
async def get_db_session():
    """Get database session"""
    async for session in db_config.get_session():
        yield session


# Request/Response Models
class UpdateUserStatusRequest(BaseModel):
    """Request to update user status"""
    status: UserStatus = Field(..., description="New user status")
    reason: Optional[str] = Field(None, description="Reason for status change")
    verify_email: Optional[bool] = Field(None, description="Set to true to verify email (auto-set when status='active')")


class UserStatusResponse(BaseModel):
    """User status response"""
    user_id: str
    email: str
    status: str
    email_verified: bool
    auth_provider: str
    created_at: str
    last_login_at: Optional[str]
    verified_at: Optional[str]
    locked_until: Optional[str]
    failed_login_attempts: int


class StatusUpdateResponse(BaseModel):
    """Response after status update"""
    success: bool
    message: str
    user_id: str
    old_status: str
    new_status: str


@router.get("/users/{user_id}/status", response_model=UserStatusResponse)
async def get_user_status_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get user status by user ID (UUID)
    
    Returns complete user status information including:
    - Current status
    - Email verification status
    - Login history
    - Security information
    """
    try:
        # Validate UUID format
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format. Must be a valid UUID"
        )
    
    # Query user
    result = await db.execute(
        select(UserAccountORM).where(UserAccountORM.id == user_uuid)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserStatusResponse(
        user_id=str(user.id),
        email=user.email,
        status=user.status.value,
        email_verified=user.email_verified,
        auth_provider=user.auth_provider,
        created_at=user.created_at.isoformat(),
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
        verified_at=user.verified_at.isoformat() if user.verified_at else None,
        locked_until=user.locked_until.isoformat() if user.locked_until else None,
        failed_login_attempts=user.failed_login_attempts
    )


@router.get("/users/email/{email}/status", response_model=UserStatusResponse)
async def get_user_status_by_email(
    email: EmailStr,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get user status by email address
    
    Returns complete user status information
    """
    # Query user by email
    result = await db.execute(
        select(UserAccountORM).where(UserAccountORM.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    
    return UserStatusResponse(
        user_id=str(user.id),
        email=user.email,
        status=user.status.value,
        email_verified=user.email_verified,
        auth_provider=user.auth_provider,
        created_at=user.created_at.isoformat(),
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
        verified_at=user.verified_at.isoformat() if user.verified_at else None,
        locked_until=user.locked_until.isoformat() if user.locked_until else None,
        failed_login_attempts=user.failed_login_attempts
    )


@router.patch("/users/{user_id}/status", response_model=StatusUpdateResponse)
async def update_user_status(
    user_id: str,
    request: UpdateUserStatusRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update user status by user ID
    
    Valid status values:
    - active: User account is active and can login
    - inactive: User account is deactivated
    - pending_verification: Waiting for email/phone verification
    - suspended: Account suspended (temporary)
    - deleted: Account marked as deleted
    
    Provide optional reason for audit purposes
    """
    try:
        # Validate UUID format
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format. Must be a valid UUID"
        )
    
    # Query user
    result = await db.execute(
        select(UserAccountORM).where(UserAccountORM.id == user_uuid)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Store old status
    old_status = user.status.value
    
    # Update status
    user.status = request.status
    
    # Auto-verify email when setting status to active (unless explicitly disabled)
    if request.status == UserStatus.ACTIVE and request.verify_email != False:
        user.email_verified = True
        if not user.verified_at:
            user.verified_at = datetime.now(timezone.utc)
    elif request.verify_email == True:
        # Explicit email verification requested
        user.email_verified = True
        if not user.verified_at:
            user.verified_at = datetime.now(timezone.utc)
    
    # Commit changes
    await db.commit()
    await db.refresh(user)
    
    return StatusUpdateResponse(
        success=True,
        message=f"User status updated successfully{f': {request.reason}' if request.reason else ''}",
        user_id=str(user.id),
        old_status=old_status,
        new_status=user.status.value
    )


@router.patch("/users/email/{email}/status", response_model=StatusUpdateResponse)
async def update_user_status_by_email(
    email: EmailStr,
    request: UpdateUserStatusRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update user status by email address
    
    Valid status values:
    - active: User account is active and can login
    - inactive: User account is deactivated
    - pending_verification: Waiting for email/phone verification
    - suspended: Account suspended (temporary)
    - deleted: Account marked as deleted
    """
    # Query user by email
    result = await db.execute(
        select(UserAccountORM).where(UserAccountORM.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    
    # Store old status
    old_status = user.status.value
    
    # Update status
    user.status = request.status
    
    # Auto-verify email when setting status to active (unless explicitly disabled)
    if request.status == UserStatus.ACTIVE and request.verify_email != False:
        user.email_verified = True
        if not user.verified_at:
            user.verified_at = datetime.now(timezone.utc)
    elif request.verify_email == True:
        # Explicit email verification requested
        user.email_verified = True
        if not user.verified_at:
            user.verified_at = datetime.now(timezone.utc)
    
    # Commit changes
    await db.commit()
    await db.refresh(user)
    
    return StatusUpdateResponse(
        success=True,
        message=f"User status updated successfully{f': {request.reason}' if request.reason else ''}",
        user_id=str(user.id),
        old_status=old_status,
        new_status=user.status.value
    )
