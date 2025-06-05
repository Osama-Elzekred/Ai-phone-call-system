"""Base database models and utilities."""

from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declared_attr

from .session import Base


class TimestampMixin:
    """Mixin for timestamp fields."""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """Mark record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now()


class TenantMixin:
    """Mixin for multi-tenant support."""
    
    tenant_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)


class BaseEntity(Base):
    """Base entity with common fields."""
    
    __abstract__ = True
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class BaseModel(BaseEntity, TimestampMixin, SoftDeleteMixin):
    """Base model with all mixins."""
    
    __abstract__ = True


class TenantBaseModel(BaseModel, TenantMixin):
    """Base model for tenant-specific entities."""
    
    __abstract__ = True
