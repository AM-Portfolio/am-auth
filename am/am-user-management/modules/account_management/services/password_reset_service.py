"""Password Reset Service"""
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from modules.account_management.infrastructure.models.user_account_orm import UserAccountORM
from modules.account_management.infrastructure.models.password_reset_token_orm import PasswordResetTokenORM
from modules.account_management.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher

logger = logging.getLogger(__name__)


class PasswordResetService:
    """Service for handling password reset operations"""
    
    def __init__(self, db: AsyncSession, password_hasher: BcryptPasswordHasher):
        self.db = db
        self.password_hasher = password_hasher
    
    async def request_reset(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Request a password reset for a user
        
        Args:
            email: User's email address
            
        Returns:
            Tuple[success: bool, message: str, reset_token: Optional[str]]
        """
        try:
            # Find user by email
            result = await self.db.execute(
                select(UserAccountORM).where(UserAccountORM.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                # For security, don't reveal if user exists
                return True, "If an account exists with this email, a reset link will be sent", None
            
            # Revoke any existing reset tokens
            result = await self.db.execute(
                select(PasswordResetTokenORM).where(
                    PasswordResetTokenORM.user_id == user.id,
                    PasswordResetTokenORM.is_used == False,
                    PasswordResetTokenORM.is_revoked == False
                )
            )
            existing_tokens = result.scalars().all()
            for token in existing_tokens:
                token.is_revoked = True
            
            # Create new reset token
            reset_token = PasswordResetTokenORM.create_for_user(
                user_id=str(user.id),
                expiration_hours=24
            )
            
            self.db.add(reset_token)
            await self.db.commit()
            
            logger.info(f"Password reset token created for user: {user.email}", extra={
                "user_id": str(user.id),
                "token_id": str(reset_token.id)
            })
            
            return True, "If an account exists with this email, a reset link will be sent", reset_token.token
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {e}", exc_info=True)
            return False, "Error processing reset request", None
    
    async def validate_reset_token(self, email: str, token: str) -> Tuple[bool, str]:
        """
        Validate a reset token
        
        Args:
            email: User's email address
            token: Reset token
            
        Returns:
            Tuple[is_valid: bool, message: str]
        """
        try:
            # Find user
            result = await self.db.execute(
                select(UserAccountORM).where(UserAccountORM.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False, "User not found"
            
            # Find valid reset token
            result = await self.db.execute(
                select(PasswordResetTokenORM).where(
                    PasswordResetTokenORM.user_id == user.id,
                    PasswordResetTokenORM.token == token
                )
            )
            reset_token = result.scalar_one_or_none()
            
            if not reset_token:
                return False, "Invalid reset token"
            
            # Check if token is valid
            if not reset_token.is_valid():
                reason = "Token expired" if reset_token.expires_at <= datetime.now(timezone.utc) else "Token already used or revoked"
                return False, reason
            
            return True, "Token is valid"
            
        except Exception as e:
            logger.error(f"Error validating reset token: {e}", exc_info=True)
            return False, "Error validating token"
    
    async def reset_password(self, email: str, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset user password using a valid token
        
        Args:
            email: User's email address
            token: Reset token
            new_password: New password
            
        Returns:
            Tuple[success: bool, message: str]
        """
        try:
            # Validate token first
            is_valid, validation_message = await self.validate_reset_token(email, token)
            if not is_valid:
                logger.warning(f"Invalid token attempt for {email}: {validation_message}")
                return False, validation_message
            
            # Find user
            result = await self.db.execute(
                select(UserAccountORM).where(UserAccountORM.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False, "User not found"
            
            # Hash new password
            password_hash = self.password_hasher.hash_password(new_password)
            
            # Update user password
            user.password_hash = password_hash
            user.updated_at = datetime.now(timezone.utc)
            
            # Find and mark token as used
            result = await self.db.execute(
                select(PasswordResetTokenORM).where(
                    PasswordResetTokenORM.user_id == user.id,
                    PasswordResetTokenORM.token == token
                )
            )
            reset_token = result.scalar_one_or_none()
            
            if reset_token:
                reset_token.is_used = True
                reset_token.used_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            
            logger.info(f"Password reset successfully for user: {email}", extra={
                "user_id": str(user.id)
            })
            
            return True, "Password reset successfully"
            
        except Exception as e:
            logger.error(f"Error resetting password: {e}", exc_info=True)
            await self.db.rollback()
            return False, "Error resetting password"
    
    async def revoke_all_tokens(self, user_id: str) -> bool:
        """
        Revoke all reset tokens for a user
        
        Args:
            user_id: User ID
            
        Returns:
            bool: Success status
        """
        try:
            result = await self.db.execute(
                select(PasswordResetTokenORM).where(
                    PasswordResetTokenORM.user_id == user_id,
                    PasswordResetTokenORM.is_used == False
                )
            )
            tokens = result.scalars().all()
            
            for token in tokens:
                token.is_revoked = True
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error revoking tokens: {e}", exc_info=True)
            return False
