"""
Configuration settings for Briefcase application.
"""
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings configuration."""
    
    # Application
    APP_NAME: str = "Briefcase"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = "1.0.0"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./briefcase_dev.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here-change-in-production")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()