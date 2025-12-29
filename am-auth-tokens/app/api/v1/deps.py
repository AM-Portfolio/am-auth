from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token, TokenData
from app.services.user_validation import user_validation_service, UserValidationService
from jose import JWTError


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Dependency to get the current user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials from request header
    
    Returns:
        TokenData object with current user information
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        return token_data
    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency to get the current active user.
    This can be extended to check if user is active/enabled.
    
    Args:
        current_user: Current user from get_current_user dependency
    
    Returns:
        TokenData object for active user
    """
    # In a real application, you might want to check if the user is still active
    # by making a call to the user management service
    return current_user


def get_user_validation_service() -> UserValidationService:
    """
    Dependency to get the user validation service.
    
    Returns:
        UserValidationService instance
    """
    return user_validation_service


def require_scopes(*required_scopes: str):
    """
    Dependency factory to require specific scopes.
    
    Args:
        required_scopes: List of required scopes
    
    Returns:
        Dependency function that validates user has required scopes
    """
    def check_scopes(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if not all(scope in current_user.scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return check_scopes