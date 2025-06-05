"""Repository interfaces for identity domain."""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from ..entities.user import User
from ..entities.tenant import Tenant


class IUserRepository(ABC):
    """User repository interface."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str, tenant_id: UUID) -> Optional[User]:
        """Get user by username within tenant."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user."""
        pass
    
    @abstractmethod
    async def list_by_tenant(
        self, 
        tenant_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """List users in a tenant."""
        pass
    
    @abstractmethod
    async def count_by_tenant(self, tenant_id: UUID) -> int:
        """Count users in a tenant."""
        pass
    
    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        pass
    
    @abstractmethod
    async def username_exists(self, username: str, tenant_id: UUID) -> bool:
        """Check if username exists in tenant."""
        pass


class ITenantRepository(ABC):
    """Tenant repository interface."""
    
    @abstractmethod
    async def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        pass
    
    @abstractmethod
    async def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name."""
        pass
    
    @abstractmethod
    async def update(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        pass
    
    @abstractmethod
    async def delete(self, tenant_id: UUID) -> bool:
        """Delete tenant."""
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """List all tenants."""
        pass
    
    @abstractmethod
    async def name_exists(self, name: str) -> bool:
        """Check if tenant name already exists."""
        pass


__all__ = ["IUserRepository", "ITenantRepository"]
