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
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "https://api.munish.org/auth")
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
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "test-google-client-id.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_JWKS_URL: str = os.getenv("GOOGLE_JWKS_URL", "https://www.googleapis.com/oauth2/v3/certs")
    GOOGLE_ISSUER: str = os.getenv("GOOGLE_ISSUER", "https://accounts.google.com")
    GOOGLE_AUTH_ENABLED: bool = os.getenv("GOOGLE_AUTH_ENABLED", "true").lower() == "true"
    GOOGLE_TOKEN_CACHE_TTL: int = int(os.getenv("GOOGLE_TOKEN_CACHE_TTL", "3600"))
    GOOGLE_EMAIL_DOMAINS_ALLOWED: str = os.getenv("GOOGLE_EMAIL_DOMAINS_ALLOWED", "")
    
    @property
    def google_allowed_domains_list(self) -> list:
        """Convert GOOGLE_EMAIL_DOMAINS_ALLOWED string to list."""
        if not self.GOOGLE_EMAIL_DOMAINS_ALLOWED:
            return []
        return [domain.strip() for domain in self.GOOGLE_EMAIL_DOMAINS_ALLOWED.split(",")]
    
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