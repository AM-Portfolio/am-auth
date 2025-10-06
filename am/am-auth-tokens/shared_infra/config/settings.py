import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    # User Management Service
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
    USER_SERVICE_TIMEOUT: int = int(os.getenv("USER_SERVICE_TIMEOUT", "30"))
    
    # API Configuration
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Auth Tokens Service")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    @property
    def allowed_origins_list(self) -> list:
        """Convert ALLOWED_ORIGINS string to list."""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()