"""Password reset API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from shared_infra.database.config import db_config
from modules.account_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.account_management.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from modules.account_management.infrastructure.services.mock_email_service import MockEmailService
from modules.account_management.application.use_cases.forgot_password import (
    ForgotPasswordUseCase,
    ForgotPasswordRequest,
    ResetPasswordWithTokenUseCase,
    ResetPasswordRequest as ResetPasswordUseCaseRequest
)

router = APIRouter(prefix="/api/v1/password", tags=["Password Reset"])


# Dependency injection
async def get_db_session():
    """Get database session dependency"""
    async for session in db_config.get_session():
        yield session


async def get_user_repository(session: AsyncSession = Depends(get_db_session)):
    """Get user repository dependency"""
    return SQLAlchemyUserRepository(session)


def get_password_hasher():
    """Get password hasher dependency"""
    return BcryptPasswordHasher()


def get_email_service():
    """Get email service dependency"""
    return MockEmailService()


# Request/Response models
class ForgotPasswordRequestModel(BaseModel):
    """Request model for forgot password"""
    email: EmailStr = Field(..., description="Email address of the account")


class ForgotPasswordResponseModel(BaseModel):
    """Response model for forgot password"""
    message: str
    email: str


class ResetPasswordRequestModel(BaseModel):
    """Request model for reset password"""
    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class ResetPasswordResponseModel(BaseModel):
    """Response model for reset password"""
    success: bool
    message: str


# Endpoints
@router.post("/forgot", response_model=ForgotPasswordResponseModel)
async def forgot_password(
    request: ForgotPasswordRequestModel,
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    email_service: MockEmailService = Depends(get_email_service),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Request a password reset link.
    
    Sends a password reset email with a token that expires in 1 hour.
    For security, always returns success even if email doesn't exist.
    """
    try:
        use_case = ForgotPasswordUseCase(
            user_repository=user_repository,
            email_service=email_service,
            db_session=session
        )
        
        result = await use_case.execute(
            ForgotPasswordRequest(email=request.email)
        )
        
        return ForgotPasswordResponseModel(
            message=result.message,
            email=result.email
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


@router.post("/reset", response_model=ResetPasswordResponseModel)
async def reset_password(
    request: ResetPasswordRequestModel,
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher)
):
    """
    Reset password using the token from email.
    
    The token expires after 1 hour. After successful reset,
    the user can login with their new password.
    """
    try:
        use_case = ResetPasswordWithTokenUseCase(
            user_repository=user_repository,
            password_hasher=password_hasher
        )
        
        result = await use_case.execute(
            ResetPasswordUseCaseRequest(
                token=request.token,
                new_password=request.new_password
            )
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return ResetPasswordResponseModel(
            success=result.success,
            message=result.message
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting your password"
        )


@router.get("/verify-token/{token}")
async def verify_reset_token(token: str):
    """
    Verify if a password reset token is valid and not expired.
    
    This endpoint can be used by the frontend to check token validity
    before showing the reset password form.
    """
    try:
        import hashlib
        from datetime import datetime, timezone
        from sqlalchemy import select
        from modules.account_management.infrastructure.models.user_account_orm import UserAccountORM
        
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        
        async for session in db_config.get_session():
            stmt = select(UserAccountORM).where(
                UserAccountORM.password_reset_token == hashed_token
            )
            result = await session.execute(stmt)
            user_orm = result.scalar_one_or_none()
            
            if not user_orm:
                return {
                    "valid": False,
                    "message": "Invalid reset token"
                }
            
            if user_orm.password_reset_token_expires < datetime.now(timezone.utc):
                return {
                    "valid": False,
                    "message": "Reset token has expired"
                }
            
            return {
                "valid": True,
                "message": "Token is valid",
                "email": user_orm.email
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while verifying the token"
        )
