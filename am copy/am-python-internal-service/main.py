"""
Python Internal Service - Document Processing Service
This service handles internal document processing operations and requires authentication.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from contextlib import asynccontextmanager

# Add shared logging to path
shared_path = Path(__file__).parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from datetime import datetime, timedelta

# Initialize centralized logging (if available)
try:
    from shared.logging import initialize_user_management_logging, get_logger
    logger_instance = initialize_user_management_logging()
    logger = get_logger("am-python-internal-service.main")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("am-python-internal-service.main")

# Import shared auth utilities
try:
    from shared.auth.validation import validate_user_token, validate_service_token, validate_user_or_service_token
except ImportError:
    logger.warning("Shared auth utilities not available, using local implementation")
    # Fallback to local implementation (already defined below)

# Configuration
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-tokens:8001")

# Models
class Document(BaseModel):
    id: str
    name: str
    content: str
    processed: bool = False
    created_at: str
    user_id: str = None

class ProcessDocumentRequest(BaseModel):
    document_id: str
    processing_options: Dict[str, Any] = {}

class ProcessDocumentResponse(BaseModel):
    document_id: str
    status: str
    processing_result: Dict[str, Any]
    processed_at: str

# Mock data
MOCK_DOCUMENTS = [
    Document(
        id="doc-001",
        name="Financial Report Q1",
        content="Financial data for Q1 2024...",
        processed=True,
        created_at="2024-01-15T10:00:00Z",
        user_id="user-123"
    ),
    Document(
        id="doc-002", 
        name="User Manual Draft",
        content="User manual content...",
        processed=False,
        created_at="2024-01-16T14:30:00Z",
        user_id="user-456"
    ),
    Document(
        id="doc-003",
        name="Technical Specification",
        content="Technical specification document...",
        processed=True,
        created_at="2024-01-17T09:15:00Z",
        user_id="user-123"
    )
]

# Use shared auth validation or fallback to local if not available
try:
    # Use shared validation functions imported above
    pass
except NameError:
    # Fallback local implementation
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    import jwt
    
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here-change-in-production")
    INTERNAL_JWT_SECRET = os.getenv("INTERNAL_JWT_SECRET", "internal-service-super-secret-key-32chars-minimum-change-in-prod")
    security = HTTPBearer()

    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify JWT token from user or service"""
        try:
            token = credentials.credentials
            
            # Try user token first
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                if payload.get("type") == "user_token":
                    logger.info(f"User token validated for user: {payload.get('username')}")
                    return {"type": "user", "payload": payload}
            except jwt.JWTError:
                pass
            
            # Try service token
            try:
                payload = jwt.decode(token, INTERNAL_JWT_SECRET, algorithms=["HS256"])
                if payload.get("type") == "service_token":
                    logger.info(f"Service token validated for service: {payload.get('service_id')}")
                    return {"type": "service", "payload": payload}
            except jwt.JWTError:
                pass
                
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )

    async def validate_user_token(auth_info = Depends(verify_token)):
        """Ensure token is from a user (not service-to-service)"""
        if auth_info["type"] != "user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User token required"
            )
        return auth_info["payload"]

    async def validate_service_token(auth_info = Depends(verify_token)):
        """Ensure token is from a service"""
        if auth_info["type"] != "service":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service token required"
            )
        return auth_info["payload"]

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting Python Internal Service (Document Processor)...")
    yield
    logger.info("🛑 Shutting down Python Internal Service...")

# FastAPI app
app = FastAPI(
    title="AM Python Internal Service",
    description="Internal Document Processing Service - Requires Authentication",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Python Internal Service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Internal endpoints (auth required)
@app.get("/internal/documents", response_model=List[Document])
async def get_documents(user_payload = Depends(validate_user_token)):
    """Get list of documents for the authenticated user"""
    user_id = user_payload.get("user_id")
    
    # Filter documents by user (in real scenario, query database)
    user_documents = [doc for doc in MOCK_DOCUMENTS if doc.user_id == user_id]
    
    logger.info(f"Retrieved {len(user_documents)} documents for user {user_payload.get('username')}")
    return user_documents

@app.get("/internal/documents/all", response_model=List[Document])
async def get_all_documents(service_payload = Depends(validate_service_token)):
    """Get all documents - service-to-service endpoint"""
    service_id = service_payload.get("service_id")
    
    logger.info(f"Service {service_id} requested all documents")
    return MOCK_DOCUMENTS

@app.post("/internal/documents/process", response_model=ProcessDocumentResponse)
async def process_document(
    request: ProcessDocumentRequest,
    user_payload = Depends(validate_user_token)
):
    """Process a document"""
    user_id = user_payload.get("user_id")
    username = user_payload.get("username")
    
    # Find the document
    document = next((doc for doc in MOCK_DOCUMENTS if doc.id == request.document_id), None)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user owns the document
    if document.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Document belongs to another user"
        )
    
    # Simulate document processing
    processing_result = {
        "word_count": len(document.content.split()),
        "character_count": len(document.content),
        "processing_options_applied": request.processing_options,
        "processed_by": username,
        "processing_duration_ms": 150
    }
    
    # Update document status
    document.processed = True
    
    logger.info(f"Document {request.document_id} processed by user {username}")
    
    return ProcessDocumentResponse(
        document_id=request.document_id,
        status="completed",
        processing_result=processing_result,
        processed_at=datetime.utcnow().isoformat()
    )

@app.get("/internal/documents/{document_id}", response_model=Document)
async def get_document(document_id: str, user_payload = Depends(validate_user_token)):
    """Get a specific document"""
    user_id = user_payload.get("user_id")
    
    document = next((doc for doc in MOCK_DOCUMENTS if doc.id == document_id), None)  
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    if document.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Document belongs to another user"
        )
    
    return document

# Service info endpoint
@app.get("/internal/service-info")
async def get_service_info(service_payload = Depends(validate_service_token)):
    """Get service information - service-to-service endpoint"""
    return {
        "service_id": "am-python-internal-service",
        "service_name": "Document Processing Service",
        "version": "1.0.0",
        "capabilities": [
            "document_listing",
            "document_processing", 
            "content_analysis"
        ],
        "total_documents": len(MOCK_DOCUMENTS),
        "processed_documents": len([doc for doc in MOCK_DOCUMENTS if doc.processed])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)