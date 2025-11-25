"""
Portfolio Service Proxy
Generic proxy pattern: 1 function handles ALL endpoints to Portfolio service

Architecture:
- API Gateway validates user JWT (get_current_user)
- Generates service JWT for internal service communication
- Forwards request to Portfolio Service with service JWT + X-User-ID header
- Returns response to client

This pattern is scalable: 1 function per service, not 1 per endpoint
"""

from fastapi import APIRouter, Depends, HTTPException, Request
import httpx
import logging
from core.auth import get_current_user, generate_service_token, CurrentUser
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.api_route("/portfolio/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_portfolio_service(
    path: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Generic proxy for ALL Portfolio Service endpoints
    
    This single function handles:
    - GET /portfolio/portfolios
    - GET /portfolio/portfolios/{id}
    - POST /portfolio/portfolios
    - PUT /portfolio/portfolios/{id}
    - DELETE /portfolio/portfolios/{id}
    - GET /portfolio/analytics
    - GET /portfolio/market-data
    - ... and any future endpoints added to Portfolio Service
    
    Flow:
    1. get_current_user validates user JWT ✅
    2. Generate service JWT for inter-service communication
    3. Forward request with service JWT + X-User-ID header
    4. Return response to client
    """
    
    try:
        # Generate service token for inter-service communication
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id=settings.PORTFOLIO_SERVICE_ID,
            permissions=["portfolio:all"]
        )
        
        # Read request body for POST/PUT requests
        body = b""
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Forward request to Portfolio Service
        async with httpx.AsyncClient(timeout=settings.LONG_TIMEOUT) as client:
            response = await client.request(
                method=request.method,
                url=f"{settings.PORTFOLIO_SERVICE_URL}/api/v1/portfolio/{path}",
                headers={
                    "Authorization": f"Bearer {service_token}",
                    "X-User-ID": str(current_user.user_id),
                    "Content-Type": request.headers.get("content-type", "application/json")
                },
                content=body,
                params=request.query_params
            )
        
        # Return response from Portfolio Service
        if response.status_code >= 400:
            logger.warning(
                f"Portfolio Service error: {response.status_code} for path: {path}",
                extra={"user_id": current_user.user_id}
            )
        
        # Return JSON response or text based on content type
        if "application/json" in response.headers.get("content-type", ""):
            return response.json()
        return response.text
        
    except httpx.ConnectError:
        logger.error(
            f"Cannot connect to Portfolio Service at {settings.PORTFOLIO_SERVICE_URL}",
            extra={"user_id": current_user.user_id}
        )
        raise HTTPException(
            status_code=503,
            detail="Portfolio Service unavailable"
        )
    except Exception as e:
        logger.error(
            f"Error proxying to portfolio service: {e}",
            extra={"user_id": current_user.user_id},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
