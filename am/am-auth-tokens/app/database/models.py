"""Database models for OAuth 2.0 authorization"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ARRAY, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as GUID
from .base import Base


class AuthorizationCodeORM(Base):
    """SQLAlchemy ORM model for OAuth 2.0 authorization codes"""
    
    __tablename__ = "authorization_codes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    code = Column(String(128), unique=True, nullable=False, index=True)
    service_id = Column(String(64), nullable=False, index=True)
    consumer_key = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    
    scopes = Column(ARRAY(String), nullable=False)
    redirect_uri = Column(String(255), nullable=False)
    
    pkce_code_challenge = Column(String(128), nullable=True)
    pkce_code_challenge_method = Column(String(10), nullable=True)
    
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<AuthorizationCodeORM(code={self.code[:8]}..., service_id={self.service_id}, is_used={self.is_used})>"


class TokenRecordORM(Base):
    """SQLAlchemy ORM model for issued access tokens (for revocation tracking)"""
    
    __tablename__ = "token_records"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    jti = Column(String(64), unique=True, nullable=False, index=True)
    token_hash = Column(String(128), nullable=False)
    
    user_id = Column(String(64), nullable=False, index=True)
    service_id = Column(String(64), nullable=True, index=True)
    consumer_key = Column(String(64), nullable=True, index=True)
    
    scopes = Column(ARRAY(String), nullable=False)
    token_type = Column(String(20), default="access", nullable=False)
    
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<TokenRecordORM(jti={self.jti}, user_id={self.user_id}, is_revoked={self.is_revoked})>"


class RefreshTokenORM(Base):
    """SQLAlchemy ORM model for refresh tokens"""
    
    __tablename__ = "refresh_tokens"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    
    scopes = Column(ARRAY(String), nullable=False, default=[])
    
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    replaced_by = Column(String(255), nullable=True)  # For token rotation
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<RefreshTokenORM(user_id={self.user_id}, is_revoked={self.is_revoked})>"
