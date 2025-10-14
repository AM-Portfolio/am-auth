"""
Documents API endpoints
Proxies requests to am-python-internal-service
"""

from fastapi import APIRouter, Depends, HTTPException, Request
import httpx
import logging

from core.auth import get_current_user, generate_service_token, CurrentUser
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/documents")
async def get_user_documents(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get documents for current user
    
    ✅ PUBLIC ENDPOINT - Clients call this
    
    Flow:
    1. Validates user token
    2. Generates service token
    3. Calls internal Python service
    4. Returns documents to client
    """
    try:
        logger.info(f"User {current_user.user_id} requesting documents")
        
        # Call internal Python service with user token
        # Note: /internal/documents requires user token, not service token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.PYTHON_SERVICE_URL}/internal/documents",
                headers={"Authorization": f"Bearer {current_user.token}"},
                timeout=settings.DEFAULT_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Internal service error: {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch documents"
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Document service unavailable"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/all")
async def get_all_documents(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get all documents (requires admin permission)
    
    ✅ PUBLIC ENDPOINT
    """
    try:
        # Check admin permission
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id="api-gateway",
            permissions=["read:all_documents"]
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.PYTHON_SERVICE_URL}/internal/documents/all",
                headers={"Authorization": f"Bearer {service_token}"},
                timeout=settings.DEFAULT_TIMEOUT
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch documents"
                )
            
            return response.json()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/service-info")
async def get_document_service_info(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get document service information
    
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
                f"{settings.PYTHON_SERVICE_URL}/internal/service-info",
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
