from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import logging


class Settings(BaseSettings):
    PROJECT_NAME: str = "Lịch Báo Giảng API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    DATABASE_URL: Optional[str] = None
    USE_SQLITE: bool = True
    SQLITE_DB_PATH: str = "lbg.db"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    
    @classmethod
    def generate_secret_key(cls) -> str:
        return secrets.token_urlsafe(32)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.SECRET_KEY == "change-this-secret-key-in-production":
            logging.warning(
                "Using default SECRET_KEY. Please set SECRET_KEY in environment variables for production!"
            )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
