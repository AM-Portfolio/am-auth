from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.api import api_router, test_router
from shared_infra.config.settings import settings
from app.database.config import db_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    print("🚀 Starting Auth Tokens API...")
    
    try:
        await db_config.create_tables()
        print("✅ PostgreSQL database tables created successfully")
    except Exception as e:
        print(f"⚠️ Failed to create database tables: {e}")
        print("💡 Service will continue but OAuth 2.0 features may not work")
    
    yield
    
    print("🛑 Shutting down Auth Tokens API...")
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(test_router)  # Test routes for Google OAuth testing


@app.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
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