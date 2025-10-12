"""
API Gateway Service
Acts as a single entry point for all client requests
Proxies to internal microservices with security, rate limiting, and monitoring
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from api.v1.endpoints import documents, reports, portfolio, trades, market_data
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.logging_middleware import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AM API Gateway",
    description="Central API Gateway for Asset Management System - Single entry point for all client requests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
app.add_middleware(LoggingMiddleware)

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
    return {
        "service": "AM API Gateway",
        "version": "1.0.0",
        "description": "Central API Gateway for all microservices",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "documents": "/api/v1/documents",
            "reports": "/api/v1/reports",
            "portfolio": "/api/v1/portfolio",
            "trades": "/api/v1/trades",
            "market_data": "/api/v1/market-data"
        },
        "note": "All endpoints require authentication via Bearer token"
    }

# Register routers
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
app.include_router(portfolio.router, prefix="/api/v1", tags=["Portfolio"])
app.include_router(trades.router, prefix="/api/v1", tags=["Trades"])
app.include_router(market_data.router, prefix="/api/v1", tags=["Market Data"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
