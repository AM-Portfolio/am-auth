from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Import infrastructure components
from shared_infra.database.config import db_config
from shared_infra.events.mock_event_bus import MockEventBus
from modules.account_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.account_management.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from modules.account_management.infrastructure.services.mock_email_service import MockEmailService
from modules.account_management.application.use_cases.create_user import CreateUserUseCase
from modules.account_management.application.use_cases.login import LoginUseCase
from modules.account_management.application.use_cases.reset_password import ResetPasswordUseCase

# Dependency injection setup
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency"""
    async for session in db_config.get_session():
        yield session


async def get_user_repository(session: AsyncSession = Depends(
    get_db_session)) -> SQLAlchemyUserRepository:
    """Get user repository dependency"""
    return SQLAlchemyUserRepository(session)


def get_password_hasher() -> BcryptPasswordHasher:
    """Get password hasher dependency"""
    return BcryptPasswordHasher()


def get_email_service() -> MockEmailService:
    """Get email service dependency"""
    return MockEmailService()


def get_event_bus() -> MockEventBus:
    """Get event bus dependency"""
    return MockEventBus()


async def get_create_user_use_case(
        user_repository: SQLAlchemyUserRepository = Depends(
            get_user_repository),
        password_hasher: BcryptPasswordHasher = Depends(get_password_hasher),
        email_service: MockEmailService = Depends(get_email_service),
        event_bus: MockEventBus = Depends(get_event_bus)) -> CreateUserUseCase:
    """Get create user use case dependency"""
    return CreateUserUseCase(user_repository, password_hasher, email_service,
                             event_bus)


async def get_login_use_case(
        user_repository: SQLAlchemyUserRepository = Depends(
            get_user_repository),
        password_hasher: BcryptPasswordHasher = Depends(get_password_hasher),
        event_bus: MockEventBus = Depends(get_event_bus)) -> LoginUseCase:
    """Get login use case dependency"""
    return LoginUseCase(user_repository, password_hasher, event_bus)


async def get_reset_password_use_case(
        user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
        email_service: MockEmailService = Depends(get_email_service)) -> ResetPasswordUseCase:
    """Get reset password use case dependency"""
    return ResetPasswordUseCase(user_repository, email_service)
