"""
Reports API endpoints
Proxies requests to am-java-internal-service
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
import httpx
import logging

from core.auth import get_current_user, generate_service_token, CurrentUser
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/reports")
async def get_user_reports(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get reports for current user
    
    ✅ PUBLIC ENDPOINT - Clients call this
    
    Flow:
    1. Validates user token
    2. Generates service token
    3. Calls internal Java service
    4. Returns reports to client
    """
    try:
        logger.info(f"User {current_user.user_id} requesting reports")
        
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id="api-gateway",
            permissions=["read:reports"]
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.JAVA_SERVICE_URL}/internal/reports",
                headers={"Authorization": f"Bearer {service_token}"},
                timeout=settings.DEFAULT_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Internal service error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch reports"
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Report service unavailable"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/all")
async def get_all_reports(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get all reports (requires admin permission)
    
    ✅ PUBLIC ENDPOINT
    """
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id="api-gateway",
            permissions=["read:all_reports"]
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.JAVA_SERVICE_URL}/internal/reports/all",
                headers={"Authorization": f"Bearer {service_token}"},
                timeout=settings.DEFAULT_TIMEOUT
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch reports"
                )
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports/generate")
async def generate_report(
    report_data: Dict[str, Any],
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Generate new report
    
    ✅ PUBLIC ENDPOINT
    """
    try:
        logger.info(f"User {current_user.user_id} generating report")
        
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id="api-gateway",
            permissions=["write:reports"]
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.JAVA_SERVICE_URL}/internal/reports/generate",
                headers={"Authorization": f"Bearer {service_token}"},
                json=report_data,
                timeout=settings.LONG_TIMEOUT  # Reports might take longer
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to generate report"
                )
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/service-info")
async def get_report_service_info(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get report service information
    
    ✅ PUBLIC ENDPOINT
    """
    try:
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id="api-gateway",
            permissions=["read:service_info"]
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.JAVA_SERVICE_URL}/internal/service-info",
                headers={"Authorization": f"Bearer {service_token}"},
                timeout=settings.DEFAULT_TIMEOUT
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch service info"
                )
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
