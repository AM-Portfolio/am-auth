"""SQLAlchemy ORM model for Password Reset Tokens"""
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, CHAR
import uuid
import secrets

from modules.account_management.infrastructure.models.user_account_orm import Base, GUID


class PasswordResetTokenORM(Base):
    """SQLAlchemy ORM model for password reset tokens"""
    
    __tablename__ = "password_reset_tokens"
    
    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user
    user_id = Column(GUID(), ForeignKey('user_accounts.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Token details
    token = Column(String(255), unique=True, nullable=False, index=True)
    token_hash = Column(String(255), nullable=False)  # Store hashed version for security
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<PasswordResetTokenORM(id={self.id}, user_id={self.user_id}, is_used={self.is_used})>"
    
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        now = datetime.now(timezone.utc)
        return (
            not self.is_used and
            not self.is_revoked and
            self.expires_at > now
        )
    
    @staticmethod
    def generate_token() -> str:
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash token for storage (simple implementation)"""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()
    
    @classmethod
    def create_for_user(cls, user_id: str, expiration_hours: int = 24) -> "PasswordResetTokenORM":
        """Create a new reset token for a user"""
        token = cls.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
        
        return cls(
            user_id=user_id,
            token=token,
            token_hash=cls.hash_token(token),
            expires_at=expires_at
        )

