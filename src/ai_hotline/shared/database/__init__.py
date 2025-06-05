"""Database package exports."""

from .session import (
    Base,
    init_database,
    close_database,
    get_db,
    get_db_context,
    get_engine,
    create_database_engine,
    create_session_maker,
)

from .models import (
    TimestampMixin,
    SoftDeleteMixin,
    TenantMixin,
    BaseEntity,
    BaseModel,
    TenantBaseModel,
)

__all__ = [
    # Session management
    "Base",
    "init_database",
    "close_database",
    "get_db",
    "get_db_context",
    "get_engine",
    "create_database_engine",
    "create_session_maker",
    
    # Model mixins and bases
    "TimestampMixin",
    "SoftDeleteMixin",
    "TenantMixin",
    "BaseEntity",
    "BaseModel",
    "TenantBaseModel",
]
