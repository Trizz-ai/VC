"""
Application configuration using Pydantic Settings
"""

import os
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Verified Compliance API"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_TOKEN_EXPIRE_MINUTES: int = 15
    PUBLIC_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")
    REDIS_POOL_SIZE: int = 10
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # CORS
    CORS_ORIGINS: str = Field(default="*", env="CORS_ORIGINS")
    ALLOWED_HOSTS: str = Field(default="*", env="ALLOWED_HOSTS")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # GPS Configuration
    GPS_VERIFICATION_THRESHOLD: float = 200.0  # meters
    GPS_ACCURACY_THRESHOLD: float = 50.0  # meters
    
    # External Services
    GHL_API_KEY: Optional[str] = Field(default=None, env="GHL_API_KEY")
    GHL_LOCATION_ID: Optional[str] = Field(default=None, env="GHL_LOCATION_ID")
    GHL_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="GHL_WEBHOOK_SECRET")
    
    GOOGLE_MAPS_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_MAPS_API_KEY")
    
    SENDGRID_API_KEY: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL: str = Field(default="noreply@verifiedcompliance.com", env="SENDGRID_FROM_EMAIL")
    
    # Firebase Cloud Messaging
    FCM_SERVER_KEY: Optional[str] = Field(default=None, env="FCM_SERVER_KEY")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    LOGTAIL_TOKEN: Optional[str] = Field(default=None, env="LOGTAIL_TOKEN")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # File Storage
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_TYPES: List[str] = Field(default=["jpg", "jpeg", "png", "pdf", "doc", "docx"], env="ALLOWED_FILE_TYPES")
    
    # Email Templates
    EMAIL_TEMPLATES_DIR: str = "app/email_templates"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            return ",".join(v)
        return "*"
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            return ",".join(v)
        return "*"
    
    @validator("ENVIRONMENT", pre=True)
    def validate_environment(cls, v):
        if v not in ["development", "production", "testing"]:
            raise ValueError("ENVIRONMENT must be one of: development, production, testing")
        return v
    
    @validator("DEBUG", pre=True)
    def validate_debug(cls, v, values):
        if isinstance(v, str):
            v = v.lower() in ["true", "1", "yes", "on"]
        if values.get("ENVIRONMENT") == "production" and v:
            return False  # Force DEBUG=False in production
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
