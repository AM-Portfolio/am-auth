from fastapi import APIRouter
from app.api.v1.endpoints import token, validate, google_auth, internal, auth
from app.api.v1.endpoints.test import google_test

api_router = APIRouter()
api_router.include_router(token.router, tags=["tokens"])
api_router.include_router(validate.router, tags=["validation"])
api_router.include_router(google_auth.router, tags=["google-auth"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(internal.router, prefix="/internal", tags=["internal-services"])

test_router = APIRouter(prefix="/test")
test_router.include_router(google_test.router, tags=["testing"])