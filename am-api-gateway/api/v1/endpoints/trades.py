"""
Trade Service Proxy
Generic proxy pattern: 1 function handles ALL endpoints to Trade service

Architecture:
- API Gateway validates user JWT (get_current_user)
- Generates service JWT for internal service communication
- Forwards request to Trade Service with service JWT + X-User-ID header
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




@router.api_route("/am/trade/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_trade_service(
    path: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Generic proxy for ALL Trade Microservice endpoints
    
    Gateway URL Pattern: /api/v1/am/trade/{path}
    Trade Service URL: /{path} (passes entire path as-is)
    
    Examples:
    - Gateway: GET /api/v1/am/trade/api/v1/trades/filter?portfolioIds=123
      → Trade Service: GET /api/v1/trades/filter?portfolioIds=123
    
    - Gateway: GET /api/v1/am/trade/api/v1/journal/{journalId}
      → Trade Service: GET /api/v1/journal/{journalId}
    
    - Gateway: GET /api/v1/am/trade/api/v1/portfolio/{portfolioId}
      → Trade Service: GET /api/v1/portfolio/{portfolioId}
    
    - Gateway: POST /api/v1/am/trade/api/v1/trades
      → Trade Service: POST /api/v1/trades
    
    This allows the trade microservice to have multiple API paths (trades, journal, 
    portfolio, etc.) without hardcoding each one in the gateway.
    
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
            service_id=settings.TRADE_SERVICE_ID,
            permissions=["trade:all"]
        )
        
        # Read request body for POST/PUT requests
        body = b""
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Forward entire path as-is to Trade Service
        target_url = f"{settings.TRADE_SERVICE_URL}/{path}"
        logger.info(f"Proxying to Trade Service: {target_url}")
        
        async with httpx.AsyncClient(timeout=settings.LONG_TIMEOUT) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={
                    "Authorization": f"Bearer {service_token}",
                    "X-User-ID": str(current_user.user_id),
                    "Content-Type": request.headers.get("content-type", "application/json")
                },
                content=body,
                params=request.query_params
            )
        
        # Return response from Trade Service
        if response.status_code >= 400:
            logger.warning(
                f"Trade Service error: {response.status_code} for path: {path}",
                extra={"user_id": current_user.user_id}
            )
            
        # Propagate status code and content
        from fastapi.responses import Response
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type")
        )
        
    except httpx.ConnectError:
        logger.error(
            f"Cannot connect to Trade Service at {settings.TRADE_SERVICE_URL}",
            extra={"user_id": current_user.user_id}
        )
        raise HTTPException(
            status_code=503,
            detail="Trade Service unavailable"
        )
    except Exception as e:
        logger.error(
            f"Error proxying to trade service: {e}",
            extra={"user_id": current_user.user_id},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
