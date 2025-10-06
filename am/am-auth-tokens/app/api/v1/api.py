from fastapi import APIRouter
from app.api.v1.endpoints import token, validate

api_router = APIRouter()
api_router.include_router(token.router, tags=["tokens"])
api_router.include_router(validate.router, tags=["validation"])