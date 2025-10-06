from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.security import verify_token, get_token_expiration, TokenValidationResponse
from jose import JWTError


router = APIRouter()


class ValidateTokenRequest(BaseModel):
    token: str


class ValidateTokenResponse(BaseModel):
    valid: bool
    user_id: str = None
    username: str = None
    email: str = None
    scopes: list[str] = []
    expires_at: str = None
    message: str = None


@router.post("/validate", response_model=ValidateTokenResponse)
async def validate_token(request: ValidateTokenRequest):
    """
    Validate a JWT token and return user information.
    
    Args:
        request: Token validation request containing the token to validate
    
    Returns:
        ValidateTokenResponse with validation result and user data
    """
    try:
        # Verify the token
        token_data = verify_token(request.token)
        
        # Get expiration time
        expires_at = get_token_expiration(request.token)
        expires_at_str = expires_at.isoformat() if expires_at else None
        
        return ValidateTokenResponse(
            valid=True,
            user_id=token_data.user_id,
            username=token_data.username,
            email=token_data.email,
            scopes=token_data.scopes,
            expires_at=expires_at_str,
            message="Token is valid"
        )
    
    except JWTError as e:
        return ValidateTokenResponse(
            valid=False,
            message=f"Token validation failed: {str(e)}"
        )
    except Exception as e:
        return ValidateTokenResponse(
            valid=False,
            message=f"Unexpected error: {str(e)}"
        )


@router.post("/validate/bearer")
async def validate_bearer_token(request: ValidateTokenRequest):
    """
    Validate a bearer token (alternative endpoint format).
    
    Args:
        request: Token validation request containing the token to validate
    
    Returns:
        Dictionary with validation result
    """
    result = await validate_token(request)
    return result.dict()


@router.get("/validate/me", response_model=ValidateTokenResponse)
async def validate_current_token(token: str):
    """
    Validate token passed as query parameter.
    
    Args:
        token: JWT token as query parameter
    
    Returns:
        ValidateTokenResponse with validation result
    """
    request = ValidateTokenRequest(token=token)
    return await validate_token(request)