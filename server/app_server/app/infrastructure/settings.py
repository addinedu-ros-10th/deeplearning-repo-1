"""
Application Settings

Configuration management using Pydantic settings.
This module handles all application configuration.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    
    app_url: str = Field(..., env="DB_APP_URL")
    legacy_url: str = Field(..., env="DB_LEGACY_URL")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration"""
    
    url: str = Field(..., env="REDIS_URL")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    
    class Config:
        env_prefix = "REDIS_"


class SchedulerSettings(BaseSettings):
    """Scheduler configuration"""
    
    timezone: str = Field(default="UTC", env="SCHEDULER_TIMEZONE")
    max_workers: int = Field(default=4, env="SCHEDULER_MAX_WORKERS")
    coalesce: bool = Field(default=True, env="SCHEDULER_COALESCE")
    
    class Config:
        env_prefix = "SCHEDULER_"


class APISettings(BaseSettings):
    """API configuration"""
    
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=False, env="API_RELOAD")
    v1_str: str = Field(default="/api/v1", env="API_V1_STR")
    
    class Config:
        env_prefix = "API_"


class SecuritySettings(BaseSettings):
    """Security configuration"""
    
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    class Config:
        env_prefix = "SECURITY_"


class CORSSettings(BaseSettings):
    """CORS configuration"""
    
    origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    class Config:
        env_prefix = "CORS_"


class LoggingSettings(BaseSettings):
    """Logging configuration"""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    class Config:
        env_prefix = "LOG_"


class FileStorageSettings(BaseSettings):
    """File storage configuration"""
    
    base_dir: str = Field(..., env="FILES_BASE_DIR")
    max_size: int = Field(default=10485760, env="FILES_MAX_SIZE")  # 10MB
    allowed_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "application/pdf", "text/plain"],
        env="FILES_ALLOWED_TYPES"
    )
    
    class Config:
        env_prefix = "FILES_"


class AdminSettings(BaseSettings):
    """Admin configuration"""
    
    username: str = Field(..., env="ADMIN_USERNAME")
    password: str = Field(..., env="ADMIN_PASSWORD")
    email: str = Field(..., env="ADMIN_EMAIL")
    
    class Config:
        env_prefix = "ADMIN_"


class Settings(BaseSettings):
    """Main application settings"""
    
    app_env: str = Field(..., env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")
    project_name: str = Field(default="App Server", env="PROJECT_NAME")
    version: str = Field(default="1.0.0", env="VERSION")
    
    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    file_storage: FileStorageSettings = Field(default_factory=FileStorageSettings)
    admin: AdminSettings = Field(default_factory=AdminSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()
