"""Database session management."""

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from ..config import get_settings
from ..logging import get_logger

logger = get_logger("database.session")

# Create the base class for declarative models
Base = declarative_base()

# Global variables for engine and session
_engine: Engine = None
_SessionLocal: sessionmaker = None


def create_database_engine() -> Engine:
    """Create database engine with connection pooling."""
    settings = get_settings()
    
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=0,
        echo=settings.debug,  # Log SQL queries in debug mode
    )
    
    logger.info("Database engine created successfully")
    return engine


def create_session_maker(engine: Engine) -> sessionmaker:
    """Create session maker."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database tables."""
    global _engine, _SessionLocal
    
    settings = get_settings()
    
    try:
        # For table creation, use synchronous psycopg2 driver
        sync_database_url = settings.database_url.replace(
            "postgresql+asyncpg://", 
            "postgresql+psycopg2://"
        )
        
        # Create synchronous engine for table creation
        sync_engine = create_engine(sync_database_url)
        
        # Test connection first
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Import all models to ensure they're registered with Base
        # Note: These imports must be here to avoid circular imports
        from ...modules.identity.infrastructure.persistence.models import UserModel, TenantModel
        from ...modules.call_processing.infrastructure.persistence.models import CallModel, CallSessionModel
        
        # Create all tables using synchronous engine
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created")
        
        # Create async engine for runtime use
        _engine = create_database_engine()
        _SessionLocal = create_session_maker(_engine)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Set global variables to None to indicate database is not available
        _engine = None
        _SessionLocal = None
        raise


def close_database():
    """Close database connections."""
    global _engine
    
    if _engine:
        _engine.dispose()
        logger.info("Database connections closed")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Database session
        
    Raises:
        HTTPException: If database is not available
    """
    if _SessionLocal is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is not available. Please try again later."
        )
    
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database session.
    
    Yields:
        Database session
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine() -> Engine:
    """Get database engine."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine
