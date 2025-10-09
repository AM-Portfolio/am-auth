"""Google OAuth authentication endpoints for user management"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid

from ...infrastructure.models.user_account_orm import UserAccountORM
from ...domain.enums.user_status import UserStatus


router = APIRouter()


async def get_db_session():
    """Temporary DB session function - will be replaced by dependency from main"""
    from shared_infra.database.config import db_config
    async for session in db_config.get_session():
        yield session


class GoogleAuthRequest(BaseModel):
    google_id: str
    email: EmailStr
    email_verified: bool = True
    name: Optional[str] = None
    picture: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None


class GoogleAuthResponse(BaseModel):
    user_id: str
    email: str
    username: str
    status: str
    scopes: List[str]
    is_new_user: bool
    email_verified: bool


@router.post("/auth/google", response_model=GoogleAuthResponse)
async def google_authenticate(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create or update user from Google OAuth authentication
    
    This endpoint:
    1. Checks if user exists by google_id
    2. If not, checks if user exists by email
    3. Creates new user or updates existing user with Google info
    4. Returns user data for JWT token generation
    """
    try:
        existing_user = await db.execute(
            select(UserAccountORM).where(
                (UserAccountORM.google_id == request.google_id) |
                (UserAccountORM.email == request.email)
            )
        )
        user = existing_user.scalars().first()
        
        is_new_user = False
        
        if user:
            if not user.google_id:
                user.google_id = request.google_id
            
            user.auth_provider = "google"
            user.email_verified = request.email_verified
            user.last_google_login = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
            
            if request.picture:
                user.profile_picture_url = request.picture
            
            if request.provider_data:
                user.provider_data = request.provider_data
            
            if user.status == UserStatus.PENDING_VERIFICATION and request.email_verified:
                user.status = UserStatus.ACTIVE
                user.verified_at = datetime.now(timezone.utc)
        
        else:
            is_new_user = True
            user_id = uuid.uuid4()
            
            user = UserAccountORM(
                id=user_id,
                email=request.email,
                password_hash="",
                google_id=request.google_id,
                auth_provider="google",
                profile_picture_url=request.picture,
                email_verified=request.email_verified,
                provider_data=request.provider_data,
                status=UserStatus.ACTIVE if request.email_verified else UserStatus.PENDING_VERIFICATION,
                verified_at=datetime.now(timezone.utc) if request.email_verified else None,
                last_google_login=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(user)
        
        await db.commit()
        await db.refresh(user)
        
        scopes = ["read", "write"]
        if user.status == UserStatus.ACTIVE:
            scopes.append("profile")
        
        return GoogleAuthResponse(
            user_id=str(user.id),
            email=user.email,
            username=user.email,
            status=user.status.value,
            scopes=scopes,
            is_new_user=is_new_user,
            email_verified=user.email_verified
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process Google authentication: {str(e)}"
        )


@router.get("/auth/google/user/{google_id}")
async def get_user_by_google_id(
    google_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get user by Google ID"""
    try:
        result = await db.execute(
            select(UserAccountORM).where(UserAccountORM.google_id == google_id)
        )
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "user_id": str(user.id),
            "email": user.email,
            "google_id": user.google_id,
            "auth_provider": user.auth_provider,
            "status": user.status.value,
            "email_verified": user.email_verified,
            "profile_picture_url": user.profile_picture_url,
            "last_google_login": user.last_google_login.isoformat() if user.last_google_login else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )
