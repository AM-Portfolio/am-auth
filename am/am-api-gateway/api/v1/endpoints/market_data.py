"""
Market Data Service Proxy
Generic proxy pattern: 1 function handles ALL endpoints to Market Data service
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
import httpx
import logging
from core.auth import get_current_user, generate_service_token, CurrentUser
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.api_route("/market-data/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_market_data_service(
    path: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Generic proxy for ALL Market Data Service endpoints
    """
    
    try:
        # Generate service token for inter-service communication
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id=settings.MARKET_DATA_SERVICE_ID,
            permissions=["market-data:read"]
        )
        
        # Read request body for POST/PUT requests
        body = b""
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Forward request to Market Data Service
        target_url = f"{settings.MARKET_DATA_SERVICE_URL}/{path}"
        logger.info(f"Proxying to Market Data Service: {target_url}")
        
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
        
        # Log error if status >= 400
        if response.status_code >= 400:
            logger.warning(
                f"Market Data Service error: {response.status_code} for path: {path}",
                extra={"user_id": current_user.user_id}
            )
            
        # Propagate status code and content
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type")
        )
        
    except httpx.ConnectError:
        logger.error(
            f"Cannot connect to Market Data Service at {settings.MARKET_DATA_SERVICE_URL}",
            extra={"user_id": current_user.user_id}
        )
        raise HTTPException(
            status_code=503,
            detail="Market Data Service unavailable"
        )
    except Exception as e:
        logger.error(
            f"Error proxying to market data service: {e}",
            extra={"user_id": current_user.user_id},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")

@router.api_route("/brokerage/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_brokerage_service(
    path: str,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Proxy for Brokerage Calculator endpoints
    """
    
    try:
        # Generate service token
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id=settings.MARKET_DATA_SERVICE_ID,
            permissions=["market-data:read"]
        )
        
        # Read request body
        body = b""
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Forward request to Market Data Service (Brokerage Controller)
        target_url = f"{settings.MARKET_DATA_SERVICE_URL}/api/v1/brokerage/{path}"
        logger.info(f"Proxying to Brokerage Service: {target_url}")
        
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
        
        if response.status_code >= 400:
            logger.warning(
                f"Brokerage Service error: {response.status_code} for path: {path}",
                extra={"user_id": current_user.user_id}
            )
            
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type")
        )
        
    except httpx.ConnectError:
        logger.error(f"Cannot connect to Market Data Service at {settings.MARKET_DATA_SERVICE_URL}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Error proxying to brokerage service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
