"""
Document Processor Service Proxy
Routes requests to Java document processor service
"""

from fastapi import APIRouter, Depends, HTTPException
import httpx
import logging
from core.auth import get_current_user, generate_service_token, CurrentUser
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/documents/types")
async def get_document_types(current_user = Depends(get_current_user)):
    """
    Get available document types from Document Processor service
    
    Flow:
    1. User JWT validated by get_current_user ✅
    2. Generate service JWT for document processor
    3. Call Java service with service token
    4. Return document types to client
    """
    
    try:
        # Generate service token for inter-service communication
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id=settings.DOCUMENT_PROCESSOR_SERVICE_ID,
            permissions=["read:document-types"]
        )
        
        # Call Java document processor service
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.DOCUMENT_PROCESSOR_URL}/api/v1/documents/types",
                headers={
                    "Authorization": f"Bearer {service_token}",
                    "X-User-ID": str(current_user.user_id)
                }
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Document Processor error: {response.text}"
            )
        
        return response.json()
        
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Document Processor service unavailable"
        )
    except Exception as e:
        logger.error(f"Error calling document processor: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/documents/process")
async def process_document(
    current_user = Depends(get_current_user),
    file_data: dict = None
):
    """
    Process document using Document Processor service
    
    Only authenticated users can process documents
    """
    
    try:
        service_token = await generate_service_token(
            user_token=current_user.token,
            service_id=settings.DOCUMENT_PROCESSOR_SERVICE_ID,
            permissions=["write:documents"]
        )
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.DOCUMENT_PROCESSOR_URL}/api/v1/documents/process",
                json=file_data,
                headers={
                    "Authorization": f"Bearer {service_token}",
                    "X-User-ID": str(current_user.user_id)
                }
            )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to process document"
            )
        
        return response.json()
        
    except Exception as e:
        logger.error(f"Document processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Processing failed")


@router.get("/documents/{doc_id}")
async def get_document(
    doc_id: str,
    current_user = Depends(get_current_user)
):
    """Get specific document"""
    
    service_token = await generate_service_token(
        user_token=current_user.token,
        service_id=settings.DOCUMENT_PROCESSOR_SERVICE_ID,
        permissions=["read:documents"]
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.DOCUMENT_PROCESSOR_URL}/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {service_token}"}
        )
    
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Document not found")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code)
    
    return response.json()