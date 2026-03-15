"""
API Gateway Service
Acts as a single entry point for all client requests
Proxies to internal microservices with security, rate limiting, and monitoring
"""

import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

# Add shared logging to path
shared_path = Path(__file__).parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from shared.logging import initialize_logging, get_logger, LogConfig
from shared.logging.middleware import setup_fastapi_logging

# Initialize logging
# We use a default config here, but it will pick up env vars like LOG_LEVEL
initialize_logging("am-api-gateway", LogConfig(service_name="am-api-gateway"))
logger = get_logger("am-api-gateway.main")

from api.v1.endpoints import trades, market_data, document_processor, portfolio_service, diagnostics
from middleware.rate_limiter import RateLimiterMiddleware

# Create FastAPI app
app = FastAPI(
    title="AM API Gateway",
    description="Central API Gateway for Asset Management System - Single entry point for all client requests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup shared logging middleware
setup_fastapi_logging(app, service_name="am-api-gateway")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(RateLimiterMiddleware)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "API Gateway",
        "version": "1.0.0",
        "timestamp": time.time()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "service": "AM API Gateway",
        "version": "1.0.0",
        "description": "Central API Gateway for all microservices",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "trades": "/am/trade/{path}",
            "portfolio": "/am/portfolio/{path}",
            "market_data": "/am/market-data/{path}",
            "documents": "/am/documents/{path}",
            "diagnostics": "/api/v1/diagnostics"
        },
        "note": "All endpoints require authentication via Bearer token"
    }

# Register routers
# Old portfolio router removed - replaced with portfolio_service generic proxy
app.include_router(trades.router, tags=["Trades"])  # No prefix - handles /am/trade/{path} directly
app.include_router(market_data.router, tags=["Market Data"])
app.include_router(document_processor.router, tags=["Document Processor"])
app.include_router(portfolio_service.router, tags=["Portfolio Service"])
app.include_router(diagnostics.router, prefix="/api/v1", tags=["System Diagnostics"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True, extra={
        "path": str(request.url),
        "error_type": type(exc).__name__
    })
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url),
            "error_type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    import uvicorn
    # log_config=None is important to let our logger handle formatting
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_config=None)
