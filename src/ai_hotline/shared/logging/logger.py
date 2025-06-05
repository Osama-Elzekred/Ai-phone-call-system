"""Logging configuration and utilities."""

import logging
import logging.config
import sys
from typing import Optional, Dict, Any
from pathlib import Path

from pydantic import BaseModel


class LogConfig(BaseModel):
    """Logging configuration model."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    enable_json: bool = False
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


def setup_logging(config: LogConfig) -> None:
    """Configure application logging."""
    
    # Create formatters
    if config.enable_json:
        import json
        
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': self.formatTime(record),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add exception info if present
                if record.exc_info:
                    log_entry['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry, ensure_ascii=False)
        
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(config.format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, config.level.upper()))
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if config.file_path:
        from logging.handlers import RotatingFileHandler
        
        log_file = Path(config.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, config.level.upper()))
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: The name of the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Convenience function for module-level usage
def get_module_logger() -> logging.Logger:
    """Get a logger for the calling module.
    
    Returns:
        Logger instance named after the calling module
    """
    import inspect
    frame = inspect.currentframe()
    if frame and frame.f_back:
        module_name = frame.f_back.f_globals.get('__name__', 'unknown')
        return get_logger(module_name)
    return get_logger('unknown')


# Application-specific loggers
def get_api_logger() -> logging.Logger:
    """Get logger for API operations."""
    return get_logger("ai_hotline.api")


def get_service_logger() -> logging.Logger:
    """Get logger for service operations."""
    return get_logger("ai_hotline.service")


def get_integration_logger() -> logging.Logger:
    """Get logger for external integrations."""
    return get_logger("ai_hotline.integration")


def get_database_logger() -> logging.Logger:
    """Get logger for database operations."""
    return get_logger("ai_hotline.database")


def get_auth_logger() -> logging.Logger:
    """Get logger for authentication operations."""
    return get_logger("ai_hotline.auth")


def get_call_logger() -> logging.Logger:
    """Get logger for call processing operations."""
    return get_logger("ai_hotline.call")


def get_audio_logger() -> logging.Logger:
    """Get logger for audio processing operations."""
    return get_logger("ai_hotline.audio")


def get_llm_logger() -> logging.Logger:
    """Get logger for LLM operations."""
    return get_logger("ai_hotline.llm")
