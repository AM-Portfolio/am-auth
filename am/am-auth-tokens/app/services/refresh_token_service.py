"""Refresh Token Service"""
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.database.models import RefreshTokenORM
from shared.logging import get_logger, LoggerMixin, log_execution_time

class RefreshTokenService(LoggerMixin):
    """Service for managing refresh tokens"""
    
    # Configuration
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    REFRESH_TOKEN_LENGTH = 64
    
    @classmethod
    def _generate_token_string(cls) -> str:
        """Generate a secure random token string"""
        alphabet = string.ascii_letters + string.digits + "-_"
        return ''.join(secrets.choice(alphabet) for _ in range(cls.REFRESH_TOKEN_LENGTH))
    
    @classmethod
    @log_execution_time("am-auth-tokens.refresh_token")
    async def create_refresh_token(
        cls, 
        db: AsyncSession, 
        user_id: str, 
        scopes: List[str]
    ) -> str:
        """
        Create a new refresh token for a user
        
        Args:
            db: Database session
            user_id: User ID
            scopes: List of scopes granted
            
        Returns:
            The refresh token string
        """
        logger = get_logger("am-auth-tokens.refresh_token")
        
        try:
            token_string = cls._generate_token_string()
            expires_at = datetime.now(timezone.utc) + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
            
            refresh_token = RefreshTokenORM(
                token=token_string,
                user_id=user_id,
                scopes=scopes,
                expires_at=expires_at,
                created_at=datetime.now(timezone.utc),
                is_revoked=False
            )
            
            db.add(refresh_token)
            await db.commit()
            
            logger.info("Created refresh token", extra={
                "user_id": user_id,
                "expires_at": str(expires_at)
            })
            
            return token_string
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create refresh token: {str(e)}", extra={
                "user_id": user_id,
                "error": str(e)
            }, exc_info=True)
            raise ValueError(f"Failed to create refresh token: {str(e)}")

    @classmethod
    @log_execution_time("am-auth-tokens.refresh_token")
    async def validate_refresh_token(
        cls, 
        db: AsyncSession, 
        token: str
    ) -> RefreshTokenORM:
        """
        Validate a refresh token
        
        Args:
            db: Database session
            token: The token string
            
        Returns:
            The RefreshTokenORM object if valid
            
        Raises:
            ValueError: If token is invalid, expired, or revoked
        """
        logger = get_logger("am-auth-tokens.refresh_token")
        
        try:
            result = await db.execute(
                select(RefreshTokenORM).where(RefreshTokenORM.token == token)
            )
            refresh_token = result.scalars().first()
            
            if not refresh_token:
                logger.warning("Invalid refresh token attempt", extra={"token_preview": token[:10] + "..."})
                raise ValueError("Invalid refresh token")
            
            if refresh_token.is_revoked:
                # Security Alert: Attempt to use revoked token!
                # This could be a token theft attempt.
                # In a high-security system, we might revoke ALL tokens for this user here.
                logger.warning("Attempt to use revoked refresh token", extra={
                    "user_id": refresh_token.user_id,
                    "token_id": str(refresh_token.id)
                })
                raise ValueError("Refresh token has been revoked")
            
            if refresh_token.expires_at < datetime.now(timezone.utc):
                logger.info("Expired refresh token used", extra={
                    "user_id": refresh_token.user_id,
                    "expired_at": str(refresh_token.expires_at)
                })
                raise ValueError("Refresh token has expired")
            
            return refresh_token
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error validating refresh token: {str(e)}", exc_info=True)
            raise ValueError(f"Error validating refresh token: {str(e)}")

    @classmethod
    @log_execution_time("am-auth-tokens.refresh_token")
    async def rotate_refresh_token(
        cls, 
        db: AsyncSession, 
        old_token_string: str
    ) -> str:
        """
        Rotate refresh token: Revoke old one, create new one (Token Rotation)
        
        Args:
            db: Database session
            old_token_string: The token being exchanged
            
        Returns:
            New refresh token string
        """
        logger = get_logger("am-auth-tokens.refresh_token")
        
        try:
            # 1. Validate old token
            old_token = await cls.validate_refresh_token(db, old_token_string)
            
            # 2. Generate new token
            new_token_string = cls._generate_token_string()
            expires_at = datetime.now(timezone.utc) + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
            
            # 3. Create new token record
            new_refresh_token = RefreshTokenORM(
                token=new_token_string,
                user_id=old_token.user_id,
                scopes=old_token.scopes,
                expires_at=expires_at,
                created_at=datetime.now(timezone.utc),
                is_revoked=False
            )
            
            # 4. Revoke old token
            old_token.is_revoked = True
            old_token.revoked_at = datetime.now(timezone.utc)
            old_token.replaced_by = new_token_string
            
            db.add(new_refresh_token)
            # db.add(old_token) # Already tracked by session
            
            await db.commit()
            
            logger.info("Rotated refresh token", extra={
                "user_id": old_token.user_id,
                "old_token_id": str(old_token.id)
            })
            
            return new_token_string
            
        except Exception as e:
            await db.rollback()
            raise ValueError(f"Token rotation failed: {str(e)}")

    @classmethod
    async def revoke_token(cls, db: AsyncSession, token: str) -> bool:
        """Revoke a refresh token (Logout)"""
        try:
            result = await db.execute(
                select(RefreshTokenORM).where(RefreshTokenORM.token == token)
            )
            refresh_token = result.scalars().first()
            
            if refresh_token and not refresh_token.is_revoked:
                refresh_token.is_revoked = True
                refresh_token.revoked_at = datetime.now(timezone.utc)
                await db.commit()
                return True
            return False
        except Exception:
            await db.rollback()
            return False

refresh_token_service = RefreshTokenService()
