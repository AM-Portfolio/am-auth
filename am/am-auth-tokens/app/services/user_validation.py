import httpx
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel
from shared_infra.config.settings import settings

# Import logging
import sys
from pathlib import Path
shared_path = Path(__file__).parent.parent.parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))
from shared.logging import get_logger

logger = get_logger("am-auth-tokens.user_validation")


class UserCredentials(BaseModel):
    username: str
    password: str


class UserValidationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    scopes: list[str] = []
    message: Optional[str] = None


class UserValidationService:
    def __init__(self):
        self.base_url = settings.USER_SERVICE_URL
        self.timeout = settings.USER_SERVICE_TIMEOUT
    
    async def validate_user_credentials(
        self, 
        credentials: UserCredentials
    ) -> UserValidationResponse:
        """
        Validate user credentials against the user management service.
        
        Args:
            credentials: User credentials to validate
        
        Returns:
            UserValidationResponse with validation result and user data
        """
        start_time = time.time()
        url = f"{self.base_url}/api/v1/auth/login"
        
        logger.info(f"🔗 Calling user management service for validation", extra={
            "service": "user-management",
            "url": url,
            "username": credentials.username,
            "timeout": self.timeout
        })
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                request_start = time.time()
                response = await client.post(
                    url,
                    json={
                        "email": credentials.username,  # Assuming username is email
                        "password": credentials.password
                    },
                    headers={
                        "Content-Type": "application/json"
                    }
                )
                request_duration = (time.time() - request_start) * 1000
                
                logger.info(f"📡 User management service responded", extra={
                    "service": "user-management",
                    "status_code": response.status_code,
                    "duration_ms": round(request_duration, 2),
                    "username": credentials.username
                })
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ User credentials validated successfully", extra={
                        "user_id": data.get("user_id"),
                        "username": data.get("username"),
                        "email": data.get("email"),
                        "status": data.get("status"),
                        "scopes": data.get("scopes", []),
                        "duration_ms": round((time.time() - start_time) * 1000, 2)
                    })
                    return UserValidationResponse(
                        valid=True,
                        user_id=data.get("user_id"),
                        username=data.get("username"),
                        email=data.get("email"),
                        status=data.get("status"),
                        scopes=data.get("scopes", []),
                        message="User validated successfully"
                    )
                elif response.status_code == 401:
                    logger.warning(f"❌ Invalid credentials for user", extra={
                        "username": credentials.username,
                        "status_code": 401
                    })
                    return UserValidationResponse(
                        valid=False,
                        message="Invalid credentials"
                    )
                elif response.status_code == 404:
                    logger.warning(f"❌ User not found", extra={
                        "username": credentials.username,
                        "status_code": 404
                    })
                    return UserValidationResponse(
                        valid=False,
                        message="User not found"
                    )
                else:
                    logger.error(f"❌ User service error", extra={
                        "username": credentials.username,
                        "status_code": response.status_code,
                        "response": response.text[:200] if response.text else None
                    })
                    return UserValidationResponse(
                        valid=False,
                        message=f"User service error: {response.status_code}"
                    )
        
        except httpx.TimeoutException as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"⏱️ User service timeout", extra={
                "username": credentials.username,
                "timeout": self.timeout,
                "duration_ms": round(duration, 2),
                "error": str(e)
            })
            return UserValidationResponse(
                valid=False,
                message="User service timeout"
            )
        except httpx.RequestError as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"🔌 User service connection error", extra={
                "username": credentials.username,
                "base_url": self.base_url,
                "duration_ms": round(duration, 2),
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            return UserValidationResponse(
                valid=False,
                message=f"User service connection error: {str(e)}"
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"💥 Unexpected validation error", extra={
                "username": credentials.username,
                "duration_ms": round(duration, 2),
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            return UserValidationResponse(
                valid=False,
                message=f"Unexpected error: {str(e)}"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user information by user ID.
        
        Args:
            user_id: The user ID to look up
        
        Returns:
            User data dictionary or None if not found
        """
        start_time = time.time()
        url = f"{self.base_url}/internal/v1/users/{user_id}"
        
        logger.info(f"🔗 Fetching user by ID from user management service", extra={
            "service": "user-management",
            "url": url,
            "user_id": user_id
        })
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers={
                        "Content-Type": "application/json"
                    }
                )
                
                duration = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    logger.info(f"✅ User data retrieved successfully", extra={
                        "user_id": user_id,
                        "duration_ms": round(duration, 2),
                        "status_code": 200
                    })
                    return response.json()
                else:
                    logger.warning(f"❌ User not found or error", extra={
                        "user_id": user_id,
                        "status_code": response.status_code,
                        "duration_ms": round(duration, 2)
                    })
                    return None
        
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"💥 Error fetching user by ID", extra={
                "user_id": user_id,
                "duration_ms": round(duration, 2),
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            return None


# Global instance
user_validation_service = UserValidationService()