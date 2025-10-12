"""Configuration settings for API Gateway"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """API Gateway configuration"""
    
    # Service URLs (internal Docker network)
    PYTHON_SERVICE_URL: str = "http://am-python-internal-service:8002"
    JAVA_SERVICE_URL: str = "http://am-java-internal-service:8003"
    AUTH_SERVICE_URL: str = "http://auth-tokens:8001"
    USER_MGMT_SERVICE_URL: str = "http://am-user-management:8000"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "jwt-super-secret-signing-key-change-in-production-must-be-32chars-minimum-xyz"
    JWT_ALGORITHM: str = "HS256"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # Timeouts
    DEFAULT_TIMEOUT: float = 30.0
    LONG_TIMEOUT: float = 60.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
