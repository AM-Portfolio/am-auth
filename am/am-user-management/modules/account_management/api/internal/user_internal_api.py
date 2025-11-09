from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from shared_infra.database.config import db_config
from modules.account_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.account_management.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from core.value_objects.email import Email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal", tags=["Internal API"])


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


class ValidateCredentialsRequest(BaseModel):
    email: EmailStr
    password: str


class ValidateCredentialsResponse(BaseModel):
    valid: bool
    user_id: str = None
    username: str = None
    email: str = None
    status: str = None
    scopes: List[str] = []
    message: str = None


@router.post("/validate-credentials", response_model=ValidateCredentialsResponse)
async def validate_credentials(
    request: ValidateCredentialsRequest,
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher)
):
    """
    Internal endpoint for auth-tokens service to validate user credentials.
    Returns user information if credentials are valid.
    """
    try:
        logger.info(f"Validating credentials for: {request.email}")
        
        # Create Email value object for validation
        email_obj = Email(request.email)
        
        # Look up user by email (repository expects string)
        user = await user_repository.get_by_email(request.email)
        
        if not user:
            logger.warning(f"User not found: {request.email}")
            return ValidateCredentialsResponse(
                valid=False,
                message="Invalid credentials"
            )
        
        logger.info(f"User found: {request.email}, verifying password")
        
        # Verify password
        if not password_hasher.verify_password(request.password, user.password_hash):
            logger.warning(f"Invalid password for: {request.email}")
            return ValidateCredentialsResponse(
                valid=False,
                message="Invalid credentials"
            )
        
        logger.info(f"Password verified for: {request.email}")
        
        # Check if user is active
        status_value = str(user.status.value).upper()
        logger.info(f"User status: {status_value}")
        
        if status_value != "ACTIVE":
            logger.warning(f"User not active: {request.email}, status: {status_value}")
            return ValidateCredentialsResponse(
                valid=False,
                message=f"Account is not active: {status_value}"
            )
        
        # Return successful validation with user data
        logger.info(f"Credentials validated successfully for: {request.email}")
        return ValidateCredentialsResponse(
            valid=True,
            user_id=str(user.id.value),
            username=user.email.value,
            email=user.email.value,
            status=status_value,
            scopes=["read", "write"],
            message="Credentials validated successfully"
        )
        
    except ValueError as e:
        logger.error(f"ValueError in validate_credentials: {str(e)}")
        return ValidateCredentialsResponse(
            valid=False,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Exception in validate_credentials: {str(e)}", exc_info=True)
        return ValidateCredentialsResponse(
            valid=False,
            message="Internal server error"
        )
