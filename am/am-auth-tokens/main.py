import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add shared logging to path
shared_path = Path(__file__).parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from app.api.v1.api import api_router, test_router
from shared_infra.config.settings import settings
from app.database.config import db_config

# Import centralized logging
from shared.logging import initialize_auth_tokens_logging, get_logger
from shared.logging.auth_adapter import AMAuthLogger, get_auth_logger, log_user_login, log_user_logout
from shared.logging.fire_and_forget import get_fire_and_forget_handler, shutdown_global_logging, log_fire_and_forget

# Initialize logging at startup
logger_instance = initialize_auth_tokens_logging()
logger = get_logger("am-auth-tokens.main")
auth_logger = get_auth_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting Auth Tokens API...", extra={"event": "startup"})
    auth_logger.log_info("Auth Tokens service starting up", event="startup")
    
    # Initialize fire-and-forget logging
    ff_handler = get_fire_and_forget_handler()
    
    try:
        async with auth_logger.trace_context("database_initialization"):
            await db_config.create_tables()
            logger.info("✅ PostgreSQL database tables created successfully", extra={
                "event": "database_setup", 
                "status": "success"
            })
            auth_logger.log_info("Database tables created successfully", 
                                event="database_setup", status="success")
            # Fire-and-forget log
            await ff_handler.send_log_async({
                "trace_id": "startup",
                "span_id": "db-init",
                "service": "am-auth-tokens",
                "timestamp": "2024-01-01T00:00:00Z",
                "log_type": "TECHNICAL",
                "level": "INFO",
                "payload": {"message": "Database initialization completed"},
                "context": {"event": "database_setup", "status": "success"}
            })
    except Exception as e:
        logger.error(f"⚠️ Failed to create database tables: {e}", extra={
            "event": "database_setup",
            "status": "failed",
            "error": str(e)
        }, exc_info=True)
        auth_logger.log_error(f"Database setup failed: {e}", 
                             event="database_setup", status="failed", error=str(e))
        logger.warning("💡 Service will continue but OAuth 2.0 features may not work", extra={
            "event": "database_setup",
            "status": "degraded"
        })
        auth_logger.log_warn("Service continuing in degraded mode", 
                            event="database_setup", status="degraded")
    
    yield
    
    logger.info("🛑 Shutting down Auth Tokens API...", extra={"event": "shutdown"})
    auth_logger.log_info("Auth Tokens service shutting down", event="shutdown")
    
    # Shutdown fire-and-forget logging gracefully
    await shutdown_global_logging()
    await db_config.close()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="JWT Token Authentication Service with OAuth 2.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add logging middleware (before CORS)
try:
    from shared.logging.middleware import LoggingMiddleware
    app.add_middleware(
        LoggingMiddleware,
        service_name="am-auth-tokens",
        exclude_paths=["/health", "/metrics", "/docs", "/openapi.json", "/"]
    )
    logger.info("Added logging middleware", extra={"middleware": "logging"})
except ImportError:
    logger.warning("FastAPI logging middleware not available", extra={"middleware": "logging"})

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Added CORS middleware", extra={"middleware": "cors"})

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(test_router)  # Test routes for Google OAuth testing


@app.get("/")
async def root():
    """Root endpoint providing service information."""
    logger.info("📋 Root endpoint accessed", extra={
        "endpoint": "/",
        "method": "GET"
    })
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.debug("Health check", extra={
        "endpoint": "/health",
        "status": "healthy"
    })
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check endpoint accessed", extra={"endpoint": "/health"})
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION
        }
    )


@app.get("/info")
async def service_info():
    """Service information endpoint."""
    logger.info("Service info endpoint accessed", extra={
        "endpoint": "/info",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    })
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "jwt_algorithm": settings.JWT_ALGORITHM,
        "jwt_expire_minutes": settings.JWT_EXPIRE_MINUTES,
        "api_version": settings.API_V1_STR
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL if not settings.DEBUG else "debug"
    )