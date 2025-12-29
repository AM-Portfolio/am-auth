from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from pydantic import BaseModel
from shared_infra.config.settings import settings


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    service_id: Optional[str] = None
    token_type: Optional[str] = None  # "user" or "service"
    scopes: list[str] = []


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    scopes: list[str] = []
    expires_at: Optional[datetime] = None


def create_access_token(
    subject: Union[str, Any], 
    user_data: dict = None, 
    expires_delta: timedelta = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject (typically user ID) for the token
        user_data: Additional user data to include in the token
        expires_delta: Custom expiration time delta
    
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
    }
    
    if user_data:
        to_encode.update(user_data)
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token (works for both user and service tokens).
    
    Args:
        token: The JWT token string to verify
    
    Returns:
        TokenData object with decoded information
    
    Raises:
        JWTError: If the token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        subject: str = payload.get("sub")
        if subject is None:
            raise JWTError("Token missing subject")
        
        # Check if this is a service token
        if payload.get("type") == "service":
            token_data = TokenData(
                service_id=payload.get("service_id", subject),
                token_type="service",
                scopes=payload.get("scopes", [])
            )
        else:
            # User token
            token_data = TokenData(
                user_id=subject,
                username=payload.get("username"),
                email=payload.get("email"),
                token_type="user",
                scopes=payload.get("scopes", [])
            )
        return token_data
    
    except JWTError as e:
        raise JWTError(f"Token validation failed: {str(e)}")


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration datetime from a JWT token without full validation.
    
    Args:
        token: The JWT token string
    
    Returns:
        Expiration datetime or None if not found
    """
    try:
        # Decode without verification to get expiration
        unverified_payload = jwt.get_unverified_claims(token)
        exp_timestamp = unverified_payload.get("exp")
        if exp_timestamp:
            return datetime.utcfromtimestamp(exp_timestamp)
        return None
    except Exception:
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired without full validation.
    
    Args:
        token: The JWT token string
    
    Returns:
        True if expired, False otherwise
    """
    exp_time = get_token_expiration(token)
    if exp_time:
        return datetime.utcnow() > exp_time
    return True  # Assume expired if we can't determine expiration