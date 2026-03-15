"""Authentication endpoints (Refresh & Logout)"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import sys
from pathlib import Path

from app.core.security import create_access_token
from shared_infra.config.settings import settings
from app.database.config import db_config
from app.services.refresh_token_service import refresh_token_service

# Add shared logging to path if not present
shared_path = Path(__file__).parent.parent.parent.parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from shared.logging.auth_adapter import get_auth_logger, log_user_logout

logger = get_auth_logger()

router = APIRouter()


async def get_db():
    async for session in db_config.get_session():
        yield session


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str


class LogoutResponse(BaseModel):
    success: bool
    message: str


@router.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a new access token using a refresh token.
    Also rotates the refresh token (issues a new one and revokes the old one).
    """
    try:
        # 1. Rotate token (validates old one, revokes it, creates new one)
        new_refresh_token = await refresh_token_service.rotate_refresh_token(
            db, 
            request.refresh_token
        )
        
        # 2. Get user info from the *new* token record (we need to re-fetch or trust the rotation)
        # The rotation service validated the old token, so we know it was valid.
        # We need the user_id and scopes to generate the new access token.
        # Let's fetch the new token record to get this info.
        token_record = await refresh_token_service.validate_refresh_token(db, new_refresh_token)
        
        # 3. Create new access token
        user_data = {
            "scopes": token_record.scopes
        }
        
        access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=token_record.user_id,
            user_data=user_data,
            expires_delta=access_token_expires
        )
        
        logger.log_info(f"Token refreshed successfully for user: {token_record.user_id}", 
                       user_id=token_record.user_id,
                       event="token_refresh", 
                       status="success")
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60,
            refresh_token=new_refresh_token
        )
        
    except ValueError as e:
        logger.log_warn(f"Token refresh failed: {e}", event="token_refresh", status="failed", reason=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.log_error(f"Token refresh error: {e}", event="token_refresh", status="error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user by revoking their refresh token.
    """
    try:
        # Validate first to get user_id for logging (optional, might fail if already revoked)
        # But rotate_refresh_token/revoke logic might not give us user_id easily if we don't query first.
        # For logout, we just want to revoke.
        
        # We'll try to find the token to get user_id for logging
        try:
            token_record = await refresh_token_service.validate_refresh_token(db, request.refresh_token)
            user_id = token_record.user_id
        except:
            user_id = "unknown"

        success = await refresh_token_service.revoke_token(db, request.refresh_token)
        
        if success:
            if user_id != "unknown":
                await log_user_logout(user_id, "user_initiated")
            else:
                logger.log_info("Logout successful (user unknown)", event="logout", status="success")
        else:
            logger.log_warn("Logout attempted with invalid/expired token", event="logout", status="failed")
            # We return 200 even if token wasn't found/already revoked to not leak info
            pass
            
        return LogoutResponse(
            success=True,
            message="Successfully logged out"
        )
    except Exception as e:
        logger.log_error(f"Logout error: {e}", event="logout", status="error", error=str(e))
        # Still return success to user to not leak internal errors on logout
        return LogoutResponse(
            success=True,
            message="Successfully logged out"
        )
