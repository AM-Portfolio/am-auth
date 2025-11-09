"""Forgot password use cases - Request reset and confirm reset"""
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
import hashlib

from core.value_objects.email import Email
from core.interfaces.repository import UserRepository
from ..services.email_service import EmailServiceInterface
from ..services.password_hasher import PasswordHasherInterface
from ...domain.models.user_account import UserAccount


@dataclass
class ForgotPasswordRequest:
    """Request password reset"""
    email: str


@dataclass
class ForgotPasswordResponse:
    """Response for password reset request"""
    message: str
    email: str


@dataclass
class ResetPasswordRequest:
    """Reset password with token"""
    token: str
    new_password: str


@dataclass
class ResetPasswordResponse:
    """Response for password reset"""
    success: bool
    message: str


class ForgotPasswordUseCase:
    """Use case for requesting password reset"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailServiceInterface,
        db_session=None
    ):
        self._user_repository = user_repository
        self._email_service = email_service
        self._db_session = db_session
    
    async def _update_reset_token(self, user_id, hashed_token: str, expires_at):
        """Update user's reset token in database"""
        from sqlalchemy import update
        from ...infrastructure.models.user_account_orm import UserAccountORM
        
        if self._db_session:
            stmt = update(UserAccountORM).where(
                UserAccountORM.id == user_id
            ).values(
                password_reset_token=hashed_token,
                password_reset_token_expires=expires_at
            )
            await self._db_session.execute(stmt)
            await self._db_session.commit()
    
    def _generate_reset_token(self) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    def _hash_token(self, token: str) -> str:
        """Hash the token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def execute(self, request: ForgotPasswordRequest) -> ForgotPasswordResponse:
        """Execute forgot password use case"""
        # Validate input
        if not request.email:
            raise ValueError("Email is required")
        
        # Create email value object
        email = Email(request.email)
        
        # Find user by email (don't reveal if user exists or not for security)
        user = await self._user_repository.get_by_email(str(email))
        
        if user:
            # Generate reset token
            reset_token = self._generate_reset_token()
            hashed_token = self._hash_token(reset_token)
            
            # Set token expiration (1 hour from now)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            
            # Store the reset token in the user repository
            # We need to update the ORM model directly since repository doesn't have this method yet
            await self._update_reset_token(user.id.value, hashed_token, expires_at)
            
            # Send reset email with the unhashed token
            await self._email_service.send_password_reset_email(
                to=user.email,
                token=reset_token
            )
        
        # Always return success message for security (don't reveal if email exists)
        return ForgotPasswordResponse(
            message="If an account with that email exists, a password reset link has been sent.",
            email=str(email)
        )


class ResetPasswordWithTokenUseCase:
    """Use case for resetting password with token"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherInterface
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
    
    def _hash_token(self, token: str) -> str:
        """Hash the token for comparison"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def execute(self, request: ResetPasswordRequest) -> ResetPasswordResponse:
        """Execute reset password with token"""
        # Validate input
        if not request.token:
            raise ValueError("Reset token is required")
        
        if not request.new_password:
            raise ValueError("New password is required")
        
        if len(request.new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Hash the provided token
        hashed_token = self._hash_token(request.token)
        
        # Find user by reset token
        from sqlalchemy import select
        from ...infrastructure.models.user_account_orm import UserAccountORM
        from shared_infra.database.config import db_config
        
        user_orm = None
        async for session in db_config.get_session():
            stmt = select(UserAccountORM).where(
                UserAccountORM.password_reset_token == hashed_token
            )
            result = await session.execute(stmt)
            user_orm = result.scalar_one_or_none()
            
            if not user_orm:
                return ResetPasswordResponse(
                    success=False,
                    message="Invalid or expired reset token"
                )
            
            # Check if token is expired
            if user_orm.password_reset_token_expires < datetime.now(timezone.utc):
                return ResetPasswordResponse(
                    success=False,
                    message="Reset token has expired. Please request a new one."
                )
            
            # Hash the new password
            new_password_hash = self._password_hasher.hash_password(request.new_password)
            
            # Update password and clear reset token
            user_orm.password_hash = new_password_hash
            user_orm.password_reset_token = None
            user_orm.password_reset_token_expires = None
            user_orm.updated_at = datetime.now(timezone.utc)
            
            await session.commit()
            break
        
        return ResetPasswordResponse(
            success=True,
            message="Password has been reset successfully. You can now login with your new password."
        )
