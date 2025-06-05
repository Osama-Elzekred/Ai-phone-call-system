"""Application configuration settings."""

import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/ai_hotline",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # Connection pool settings
    pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="Redis connection URL"
    )
    
    # Connection pool settings
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    retry_on_timeout: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    socket_timeout: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
    
    class Config:
        env_prefix = "REDIS_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(
        default="your-super-secret-key-change-in-production",
        env="SECRET_KEY",
        description="Secret key for JWT token signing"
    )
    
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Password settings
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_uppercase: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    password_require_lowercase: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    password_require_numbers: bool = Field(default=True, env="PASSWORD_REQUIRE_NUMBERS")
    password_require_special: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")
    
    # Account lockout settings
    max_login_attempts: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    lockout_duration_minutes: int = Field(default=30, env="LOCKOUT_DURATION_MINUTES")
    
    class Config:
        env_prefix = "SECURITY_"


class APISettings(BaseSettings):
    """External API configuration settings."""
    
    # Munsit STT API
    munsit_api_key: Optional[str] = Field(default=None, env="MUNSIT_API_KEY")
    munsit_api_url: str = Field(
        default="https://api.munsit.ai/v1",
        env="MUNSIT_API_URL"
    )
    
    # ElevenLabs TTS API
    elevenlabs_api_key: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    elevenlabs_api_url: str = Field(
        default="https://api.elevenlabs.io/v1",
        env="ELEVENLABS_API_URL"
    )
    
    # OpenAI API
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_api_url: str = Field(
        default="https://api.openai.com/v1",
        env="OPENAI_API_URL"
    )
    
    # Anthropic Claude API
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_api_url: str = Field(
        default="https://api.anthropic.com/v1",
        env="ANTHROPIC_API_URL"
    )
    
    # Mistral API
    mistral_api_key: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")
    mistral_api_url: str = Field(
        default="https://api.mistral.ai/v1",
        env="MISTRAL_API_URL"
    )
    
    # API timeouts and retries
    api_timeout_seconds: int = Field(default=30, env="API_TIMEOUT_SECONDS")
    api_max_retries: int = Field(default=3, env="API_MAX_RETRIES")
    api_retry_delay_seconds: int = Field(default=1, env="API_RETRY_DELAY_SECONDS")
    
    class Config:
        env_prefix = "API_"


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    
    # Structured logging
    enable_json_logging: bool = Field(default=False, env="ENABLE_JSON_LOGGING")
    enable_correlation_id: bool = Field(default=True, env="ENABLE_CORRELATION_ID")
    
    class Config:
        env_prefix = "LOG_"


class AppSettings(BaseSettings):
    """Main application settings."""
    
    # Application info
    title: str = Field(default="AI Hotline Backend", env="APP_TITLE")
    description: str = Field(
        default="Arabic Voice Processing Platform with AI-powered call handling",
        env="APP_DESCRIPTION"
    )
    version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # File upload settings
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    allowed_file_extensions: List[str] = Field(
        default=[".pdf", ".docx", ".txt", ".wav", ".mp3", ".m4a"],
        env="ALLOWED_FILE_EXTENSIONS"
    )
    
    # Audio processing settings
    max_audio_duration_minutes: int = Field(default=30, env="MAX_AUDIO_DURATION_MINUTES")
    default_language_code: str = Field(default="ar-EG", env="DEFAULT_LANGUAGE_CODE")
    
    # Call processing settings
    max_concurrent_calls: int = Field(default=100, env="MAX_CONCURRENT_CALLS")
    call_timeout_minutes: int = Field(default=30, env="CALL_TIMEOUT_MINUTES")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    apis: APISettings = Field(default_factory=APISettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("allowed_file_extensions", mode="before")
    @classmethod
    def parse_file_extensions(cls, v):
        """Parse file extensions from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.database.database_url
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL."""
        return self.redis.redis_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get application settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def get_app_settings() -> AppSettings:
    """Alias for get_settings() for backward compatibility."""
    return get_settings()


def reload_settings() -> AppSettings:
    """Reload settings from environment (useful for testing)."""
    global _settings
    _settings = AppSettings()
    return _settings
