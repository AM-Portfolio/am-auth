"""Logging middleware"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logging middleware to track all requests
    Logs request method, path, duration, and response status
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"➡️  Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Log response
            duration = time.time() - start_time
            logger.info(
                f"⬅️  Response: {response.status_code} "
                f"| Duration: {duration:.2f}s "
                f"| Path: {request.url.path}"
            )
            
            # Add custom headers
            response.headers["X-Process-Time"] = f"{duration:.2f}"
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"❌ Error: {type(e).__name__} "
                f"| Duration: {duration:.2f}s "
                f"| Path: {request.url.path} "
                f"| Error: {str(e)}"
            )
            raise
