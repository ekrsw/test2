from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/knowledge_maintenance"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    jwt_private_key_path: str = "./keys/private_key.pem"
    jwt_public_key_path: str = "./keys/public_key.pem"
    jwt_algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Environment
    environment: str = "development"
    
    # CORS
    allow_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()