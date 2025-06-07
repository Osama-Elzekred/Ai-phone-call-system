"""
AI Hotline Backend - Main Application Entry Point

A DDD-based modular monolith for processing Arabic voice calls with AI.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import shared components
from src.ai_hotline.shared.config import get_app_settings, get_settings
from src.ai_hotline.shared.database import init_database, close_database
from src.ai_hotline.shared.logging import setup_logging, get_logger, LogConfig
from src.ai_hotline.shared.exceptions import (
    BaseAppException,
    AuthenticationError,
    AuthorizationError,
    DomainException,
    EntityNotFoundError,
)

# Import module routers
from src.ai_hotline.modules.identity.presentation.routers.auth import router as auth_router
from src.ai_hotline.shared.routers.health import router as health_router

# Setup logging first
settings = get_settings()
log_config = LogConfig(
    level=settings.logging.log_level,
    format=settings.logging.log_format,
    file_path=settings.logging.log_file_path,
    enable_json=settings.logging.enable_json_logging
)
setup_logging(log_config)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting AI Hotline Backend...")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
        
        # Check and apply migrations
        from src.ai_hotline.shared.database.migrations import check_and_apply_migrations
        migration_success = check_and_apply_migrations(auto_upgrade=settings.environment == "development")
        if migration_success:
            logger.info("Database migrations verified/applied successfully")
        else:
            logger.warning("Database migration check failed - continuing anyway")
            
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        logger.info("Continuing without database connection for development")
    
    yield
    
    # Cleanup
    logger.info("Shutting down AI Hotline Backend...")
    close_database()
    logger.info("Application shutdown complete")


# Create FastAPI application
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_app_settings()
    
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for security
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
        )
      # Global exception handlers
    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError):
        logger.warning(f"Authentication error: {exc.message}", extra={
            "error_code": exc.error_code,
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, exc: AuthorizationError):
        logger.warning(f"Authorization error: {exc.message}", extra={
            "error_code": exc.error_code,
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        )

    @app.exception_handler(EntityNotFoundError)
    async def entity_not_found_exception_handler(request: Request, exc: EntityNotFoundError):
        logger.info(f"Entity not found: {exc.message}", extra={
            "error_code": exc.error_code,
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        )

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        logger.error(f"Domain error: {exc.message}", extra={
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        )

    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException):
        logger.error(f"Application error: {exc.message}", extra={
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path,
        })
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        )
      # Health check endpoint (legacy - kept for backward compatibility)
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Basic health check endpoint."""
        from src.ai_hotline.shared.health import health_checker
        return await health_checker.basic_health_check()
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint."""
        return {
            "message": "AI Hotline Backend - Arabic Voice Processing Platform",
            "version": settings.version,
            "docs": "/docs",
            "health": "/health",
        }      # Include module routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    # app.include_router(call_router, prefix="/api/v1/calls", tags=["Call Processing"])
    # app.include_router(audio_router, prefix="/api/v1/audio", tags=["Audio Processing"])
    # app.include_router(llm_router, prefix="/api/v1/llm", tags=["LLM Processing"])
    # app.include_router(knowledge_router, prefix="/api/v1/knowledge", tags=["Knowledge Management"])
    # app.include_router(automation_router, prefix="/api/v1/automation", tags=["Automation"])
    
    logger.info("FastAPI application created successfully")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    settings = get_app_settings()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_config=None,  # Use our custom logging
    )

 