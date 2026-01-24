from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/wedding_db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "wedding_db"
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    
    # Service Configuration
    SERVICE_NAME: str = "wedding-core"
    SERVICE_PORT: int = 8000
    DEBUG: bool = True
    
    # Auth Service Configuration
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    AUTH_SERVICE_TIMEOUT: int = 10

    # Token used by this service when calling auth-service (service-to-service auth)
    # IMPORTANT: keep this secret, rotate regularly, and never log it.
    AUTH_SERVICE_TOKEN: str = "auth_service"
    
    # Header format used for auth-service calls
    # Example: header=Authorization, prefix=Bearer -> "Authorization: Bearer <base64(token)>"
    AUTH_SERVICE_TOKEN_HEADER: str = "Authorization"
    AUTH_SERVICE_TOKEN_PREFIX: str = "Bearer"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_TOKEN_EXPIRE_MINUTES: int = 30
    
    SHARED_CONTEXT_SECRET: str = "your-shared-context-secret-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()