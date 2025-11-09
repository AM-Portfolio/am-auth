import httpx
from typing import Optional, Dict, Any
from pydantic import BaseModel
from shared_infra.config.settings import settings


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
        Uses the internal validation endpoint to avoid circular dependency.
        
        Args:
            credentials: User credentials to validate
        
        Returns:
            UserValidationResponse with validation result and user data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/internal/validate-credentials",
                    json={
                        "email": credentials.username,  # Assuming username is email
                        "password": credentials.password
                    },
                    headers={
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if validation was successful
                    if data.get("valid"):
                        return UserValidationResponse(
                            valid=True,
                            user_id=data.get("user_id"),
                            username=data.get("username"),
                            email=data.get("email"),
                            status=data.get("status"),
                            scopes=data.get("scopes", []),
                            message=data.get("message", "User validated successfully")
                        )
                    else:
                        return UserValidationResponse(
                            valid=False,
                            message=data.get("message", "Invalid credentials")
                        )
                else:
                    return UserValidationResponse(
                        valid=False,
                        message=f"User service error: {response.status_code}"
                    )
        
        except httpx.TimeoutException:
            return UserValidationResponse(
                valid=False,
                message="User service timeout"
            )
        except httpx.RequestError as e:
            return UserValidationResponse(
                valid=False,
                message=f"User service connection error: {str(e)}"
            )
        except Exception as e:
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
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/internal/v1/users/{user_id}",
                    headers={
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
        
        except Exception:
            return None


# Global instance
user_validation_service = UserValidationService()