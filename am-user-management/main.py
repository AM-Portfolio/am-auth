"""Integrated FastAPI application using the modular architecture"""
import os
import sys
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

# Add shared logging to path
# Add shared logging to path
# Robustly find 'shared' directory
current_dir = Path(__file__).resolve().parent
shared_found = False
# Search up to 3 levels up
for _ in range(3):
    if (current_dir / "shared").exists():
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        shared_found = True
        break
    current_dir = current_dir.parent

if not shared_found:
    print("WARNING: 'shared' directory not found in parent path")

# Initialize centralized logging
from shared.logging import initialize_user_management_logging, get_logger

# Initialize logging at startup - this replaces the basic logging configuration
logger_instance = initialize_user_management_logging()
logger = get_logger("am-user-management.main")

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# Import our infrastructure components
from shared_infra.database.config import db_config
from shared_infra.events.mock_event_bus import MockEventBus
from modules.account_management.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from modules.account_management.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from modules.account_management.infrastructure.services.mock_email_service import MockEmailService
from modules.account_management.application.use_cases.create_user import CreateUserUseCase, CreateUserRequest, CreateUserResponse
from modules.account_management.application.use_cases.login import LoginUseCase, LoginRequest, LoginResponse

# Import dependency providers
from modules.account_management.api.dependencies import (
    get_db_session,
    get_user_repository,
    get_create_user_use_case,
    get_login_use_case,
    get_reset_password_use_case
)
from modules.account_management.application.use_cases.reset_password import ResetPasswordUseCase

# Import service registration router
from modules.account_management.api.service_registration import router as service_router
from modules.account_management.api.public.auth_router import router as auth_router
from modules.account_management.api.public.google_auth_router import router as google_auth_router
from modules.account_management.api.public.user_status_router import router as user_status_router
from modules.account_management.api.public.password_reset_router import router as password_reset_router
from modules.account_management.api.public.user_stats_router import router as user_stats_router


# Dependency injection setup


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("🚀 Starting AM User Management API...", extra={"event": "startup"})

    # Create database tables
    try:
        await db_config.create_tables()
        logger.info("✅ PostgreSQL database tables created successfully", extra={
            "event": "database_setup",
            "status": "success",
            "database_url": str(db_config.database_url).split("@")[-1]  # Hide credentials
        })
        logger.debug(f"📊 Full Database URL pattern: {db_config.database_url[:20]}...", extra={
            "event": "database_setup",
            "url_prefix": str(db_config.database_url)[:20]
        })
    except Exception as e:
        logger.error(f"❌ Failed to create PostgreSQL database tables: {e}", extra={
            "event": "database_setup",
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        logger.warning("💡 Make sure PostgreSQL is running: brew services start postgresql@15", extra={
            "event": "database_setup",
            "troubleshooting": "postgresql_not_running"
        })
        logger.warning("💡 Make sure database exists: createdb am_user_management", extra={
            "event": "database_setup", 
            "troubleshooting": "database_not_exists"
        })
        raise e  # Don't fall back to SQLite, we want PostgreSQL

    yield

    # Shutdown
    logger.info("🛑 Shutting down AM User Management API...", extra={"event": "shutdown"})
    await db_config.close()


# Create FastAPI app
app = FastAPI(
    title="AM User Management API",
    description=
    "User management system with modular architecture and real database integration",
    version="0.2.0",
    debug=True,
    lifespan=lifespan)

# Add logging middleware (before CORS)
try:
    from shared.logging.middleware import LoggingMiddleware
    app.add_middleware(
        LoggingMiddleware,
        service_name="am-user-management",
        exclude_paths=["/health", "/metrics", "/docs", "/openapi.json", "/"]
    )
    logger.info("Added logging middleware", extra={"middleware": "logging"})
except ImportError:
    logger.warning("FastAPI logging middleware not available", extra={"middleware": "logging"})

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Added CORS middleware", extra={"middleware": "cors"})

# Include routers

# ... existing code ...

# Include routers
# Include routers with standardized prefixes (without 'am-' prefix in path)
app.include_router(service_router) # Internal maintenance routes
app.include_router(auth_router, prefix="/users/account/v1")  # e.g. /users/account/v1/register
app.include_router(google_auth_router, prefix="/users/account/v1") # e.g. /users/account/v1/auth/google
app.include_router(user_status_router, prefix="/users/account/v1") # e.g. /users/account/v1/{id}/status
app.include_router(password_reset_router, prefix="/users/account/v1") # e.g. /users/account/v1/request-reset
app.include_router(user_stats_router, prefix="/users/account/v1") # e.g. /users/account/v1/stats


# Pydantic models for API requests/responses
class RegisterRequest(BaseModel):
    """User registration request"""
    email: str
    password: str
    phone_number: Optional[str] = None


class LoginRequestModel(BaseModel):
    """User login request"""
    email: str
    password: str


# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": "AM User Management API",
        "status": "running",
        "version": "0.2.0",
        "features": "Integrated with modular architecture and database"
    }


@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    try:
        # Test database connection
        from sqlalchemy import text
        await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "Application and database are running successfully",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "message": "Application is running but database connection failed",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/users/account/v1/infra/health")
async def infra_health_check():
    """Check health of all infrastructure components"""
    infra_checks = {
        "postgresql": ("am_postgresql", 5432),
        "mongodb": ("am_mongodb", 27017),
        "redis": ("am_redis", 6379),
        "influxdb": ("am_influxdb", 8086),
        "kafka": ("am_kafka", 9092),
        "zookeeper": ("am_zookeeper", 2181),
    }
    
    results = {}
    for name, (host, port) in infra_checks.items():
        try:
            # Use host.docker.internal for local dev if needed, 
            # but in docker network we use service names
            # Let's try service names first
            conn = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=2.0
            )
            _, writer = conn
            writer.close()
            await writer.wait_closed()
            results[name] = {"status": "connected", "host": host, "port": port}
        except Exception as e:
            # Fallback to localhost check if running outside docker but targetting docker ports
            try:
                conn = await asyncio.wait_for(
                    asyncio.open_connection("localhost", port),
                    timeout=1.0
                )
                _, writer = conn
                writer.close()
                await writer.wait_closed()
                results[name] = {"status": "connected (via localhost)", "host": "localhost", "port": port}
            except:
                results[name] = {"status": "disconnected", "error": str(e)}

    return {
        "status": "success" if all(r["status"].startswith("connected") for r in results.values()) else "partial_failure",
        "infrastructure": results
    }


@app.get("/users/account/v1/auth/status")
async def auth_status():
    return {
        "status":
        "Account management module fully integrated",
        "features": [
            "User registration with email verification",
            "User authentication with password hashing",
            "Domain events publishing", "Database persistence"
        ]
    }



# Add overrides for other use cases as needed, or define their providers
# app.dependency_overrides[ResetPasswordUseCase] = ... (need to define get_reset_password_use_case)

# Real authentication endpoints using our use cases
@app.post("/users/account/v1/auth/register", response_model=CreateUserResponse)
async def register(request: RegisterRequest,
                   create_user_use_case: CreateUserUseCase = Depends(
                       get_create_user_use_case)):
    """Register a new user"""
    try:
        logger.info("User registration attempt", extra={
            "email": request.email,
            "has_phone": bool(request.phone_number),
            "endpoint": "/users/v1/auth/register"
        })
        
        # Convert API request to use case request
        use_case_request = CreateUserRequest(email=request.email,
                                             password=request.password,
                                             phone_number=request.phone_number)

        # Execute use case
        response = await create_user_use_case.execute(use_case_request)
        
        logger.info("User registration successful", extra={
            "user_id": response.user_id,
            "email": request.email
        })
        
        return response

    except ValueError as e:
        logger.warning("User registration validation error", extra={
            "email": request.email,
            "error": str(e),
            "error_type": "ValueError"
        })
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
    except Exception as e:
        logger.error("User registration failed", extra={
            "email": request.email,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal server error: {str(e)}")


@app.post("/users/account/v1/auth/login")
async def login(request: LoginRequestModel,
                login_use_case: LoginUseCase = Depends(get_login_use_case)):
    """Authenticate user and return user data for token creation"""
    try:
        # Convert API request to use case request
        use_case_request = LoginRequest(email=request.email,
                                        password=request.password)

        # Execute use case (authenticate user)
        auth_response = await login_use_case.execute(use_case_request)

        # Return user data with access token
        return {
            "user_id": auth_response.user_id,
            "username": auth_response.email,  # Using email as username
            "email": auth_response.email,
            "status": auth_response.status,
            "scopes": auth_response.scopes,
            "access_token": auth_response.access_token
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
    except Exception as e:
        if "invalid" in str(e).lower() or "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid email or password")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error occurred")


# Internal API for auth-tokens service integration
@app.get("/internal/v1/users/{user_id}")
async def get_user_internal(
    user_id: str,
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)):
    """
    Internal endpoint for auth-tokens service to verify user status.
    Called when creating JWT tokens.
    """
    try:
        # Import UserId to create proper value object
        from core.value_objects.user_id import UserId

        # Create UserId object from string
        user_id_obj = UserId(user_id)

        # Look up user by user_id
        user = await user_repository.get_by_id(user_id_obj)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")

        # Return user details for JWT token creation
        status_value = str(
            user.status.value).upper()  # Ensure uppercase comparison
        is_active = status_value == "ACTIVE"

        # Determine user scopes based on email (admin users get admin scope)
        scopes = ["read", "write"]
        if user.email.value in ["admin@example.com", "ne2@example.com"]:
            scopes.append("admin")

        return {
            "user_id":
            str(user.id.value),  # Fixed: use user.id instead of user.user_id
            "username": user.email.value,  # Using email as username
            "email": user.email.value,
            "status": status_value,
            "scopes": scopes,  # Based on user roles/permissions
            "active": is_active
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error occurred")


@app.post("/internal/v1/auth/validate-credentials")
async def validate_credentials_internal(
    credentials: dict,
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)):
    """
    Internal endpoint for auth-tokens service to validate user credentials.
    This endpoint validates email/password WITHOUT calling auth-tokens service
    to avoid circular dependency.
    """
    try:
        from core.value_objects.email import Email
        from modules.account_management.application.use_cases.login import LoginUseCase
        from shared_infra.logging.logger import get_logger
        
        logger = get_logger(__name__)
        
        email_str = credentials.get("email")
        password = credentials.get("password")
        
        if not email_str or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Validate email format
        try:
            email = Email(email_str)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Find user by email
        user = await user_repository.get_by_email(email)
        
        if not user:
            logger.warning(f"Login failed: User not found for email {email_str}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check account status
        if user.status.value.upper() != "ACTIVE":
            logger.warning(f"Login failed: User {user.id.value} status is {user.status.value}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not user.verify_password(password):
            logger.warning(f"Login failed: Invalid password for user {user.id.value}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Return user data for token creation
        return {
            "user_id": str(user.id.value),
            "username": user.email.value,
            "email": user.email.value,
            "status": user.status.value.upper(),
            "scopes": ["read", "write"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during credential validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )


# Internal service-to-service endpoints
@app.get("/internal/v1/service-info")
async def get_service_info():
    """
    Internal endpoint for service discovery and health checking.
    Called by other internal services.
    """
    return {
        "service_id": "am-user-management",
        "service_name": "User Management Service",
        "version": "1.0.0",
        "capabilities": [
            "user_authentication",
            "user_registration", 
            "user_management",
            "jwt_token_validation"
        ],
        "endpoints": {
            "internal": [
                "/internal/v1/users/{user_id}",
                "/internal/v1/service-info"
            ],
            "public": [
                "/api/v1/auth/register",
                "/api/v1/auth/login", 
                "/api/v1/auth/status"
            ]
        }
    }


@app.post("/api/v1/admin/reset-database")
async def reset_database():
    """Reset database - Drop and recreate all tables (DEV ONLY)"""
    try:
        logger.warning("Database reset requested - dropping all tables", extra={
            "endpoint": "/api/v1/admin/reset-database",
            "action": "reset_database"
        })
        
        # Drop all tables
        await db_config.drop_tables()
        logger.info("All database tables dropped successfully")
        
        # Recreate all tables with current schema
        await db_config.create_tables()
        logger.info("All database tables recreated successfully")
        
        return {
            "status": "success",
            "message": "Database reset completed successfully",
            "action": "tables_dropped_and_recreated"
        }
        
    except Exception as e:
        logger.error("Database reset failed", extra={
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
