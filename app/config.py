from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DATABASE_URL: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 1
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""

    # Service Configuration
    SERVICE_NAME: str = ""
    SERVICE_PORT: int = 1
    DEBUG: bool = True

    # Auth Service Configuration
    AUTH_SERVICE_URL: str = "1"
    AUTH_SERVICE_TIMEOUT: int = 1

    # Token used by this service when calling auth-service (service-to-service auth)
    AUTH_SERVICE_TOKEN: str = ""

    # Header format used for auth-service calls
    AUTH_SERVICE_TOKEN_HEADER: str = ""
    AUTH_SERVICE_TOKEN_PREFIX: str = ""

    # JWT Configuration
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    JWT_TOKEN_EXPIRE_MINUTES: int = 1

    SHARED_CONTEXT_SECRET: str = "1"

    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Use TLS when connecting to managed Redis (e.g., AWS ElastiCache Serverless)
    # Set via env: REDIS_SSL=True
    REDIS_SSL: bool = False

    # Optional: provide a full URL (supports redis:// or rediss://)
    # If set, this takes precedence over REDIS_HOST/REDIS_PORT/REDIS_DB.
    REDIS_URL: str = ""

    # Redis Cache Hosts (Multi-instance support)
    @property
    def REDIS_CACHE_HOSTS(self) -> dict:
        """
        Multiple Redis cache configurations.
        Can be overridden by environment variable as JSON string.
        """
        return {
            "shaadi_on_track": {
                "REDIS_HOST": self.REDIS_HOST,
                "REDIS_PORT": self.REDIS_PORT,
                "REDIS_DB": self.REDIS_DB,
                "REDIS_SSL": self.REDIS_SSL,
                "REDIS_URL": self.REDIS_URL,
                "LABEL": "shaadi_on_track",
            }
        }

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = ""
    S3_BUCKET_NAME: str = ""
    S3_PRESIGNED_URL_EXPIRY: int = 1

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
