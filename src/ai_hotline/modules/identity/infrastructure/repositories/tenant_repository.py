"""SQLAlchemy implementation of tenant repository."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.ai_hotline.shared.exceptions import DatabaseError, EntityNotFoundError
from src.ai_hotline.modules.identity.domain.entities.tenant import Tenant
from src.ai_hotline.modules.identity.domain.repositories import ITenantRepository
from ..persistence.models import TenantModel
from ..mappers.user_mapper import TenantMapper


class SqlAlchemyTenantRepository(ITenantRepository):
    """SQLAlchemy implementation of tenant repository."""
    
    def __init__(self, session: Session):
        self.session = session

    async def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        try:
            tenant_model = TenantMapper.to_model(tenant)
            self.session.add(tenant_model)
            self.session.commit()
            self.session.refresh(tenant_model)
            return TenantMapper.to_domain(tenant_model)
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to create tenant: {e}")
    
    async def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        try:
            tenant_model = self.session.query(TenantModel).filter(
                and_(TenantModel.id == tenant_id)
            ).first()
            return TenantMapper.to_domain(tenant_model) if tenant_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get tenant by ID: {e}")
    
    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name."""
        try:
            tenant_model = self.session.query(TenantModel).filter(
                and_(TenantModel.name == name)
            ).first()
            return TenantMapper.to_domain(tenant_model) if tenant_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get tenant by name: {e}")
    
    async def update(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        try:
            # Get existing model
            existing_model = self.session.query(TenantModel).filter(
                TenantModel.id == tenant.id
            ).first()
            if not existing_model:
                raise EntityNotFoundError("Tenant not found")
            
            # Update model from entity
            TenantMapper.update_model_from_entity(existing_model, tenant)
            self.session.commit()
            self.session.refresh(existing_model)
            return TenantMapper.to_domain(existing_model)
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to update tenant: {e}")
    
    async def delete(self, tenant_id: UUID) -> bool:
        """Delete tenant (soft delete)."""
        try:
            tenant_model = self.session.query(TenantModel).filter(
                TenantModel.id == tenant_id
            ).first()
            if not tenant_model:
                return False
            
            # tenant_model.is_active = False
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to delete tenant: {e}")
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """List all active tenants."""
        try:
            tenant_models = self.session.query(TenantModel).offset(skip).limit(limit).all()
            return [TenantMapper.to_domain(model) for model in tenant_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list tenants: {e}")
    
    async def name_exists(self, name: str) -> bool:
        """Check if tenant name already exists."""
        try:
            count = self.session.query(TenantModel).filter(
                and_(TenantModel.name == name)
            ).count()
            return count > 0
        except Exception as e:
            raise DatabaseError(f"Failed to check tenant name existence: {e}")
    
    async def get_active_trial_tenants(self) -> List[Tenant]:
        """Get all active trial tenants."""
        try:
            tenant_models = self.session.query(TenantModel).filter(
                and_(
                    TenantModel.status == "trial"
                )
            ).all()
            return [TenantMapper.to_domain(model) for model in tenant_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get trial tenants: {e}")
    
    async def get_expired_trial_tenants(self) -> List[Tenant]:
        """Get all expired trial tenants."""
        from datetime import datetime
        try:
            tenant_models = self.session.query(TenantModel).filter(
                and_(
                    TenantModel.status == "trial",
                    TenantModel.trial_ends_at <= datetime.utcnow()
                )
            ).all()
            return [TenantMapper.to_domain(model) for model in tenant_models]
        except Exception as e:
            raise DatabaseError(f"Failed to get expired trial tenants: {e}")
    
    async def update_tenant_status(self, tenant_id: UUID, new_status: str) -> bool:
        """Update tenant status."""
        try:
            tenant_model = self.session.query(TenantModel).filter(
                TenantModel.id == tenant_id
            ).first()
            if not tenant_model:
                return False
            
            tenant_model.status = new_status
            tenant_model.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to update tenant status: {e}")
    
    async def update_tenant_limits(
        self,
        tenant_id: UUID,
        max_users: Optional[int] = None,
        max_calls_per_month: Optional[int] = None,
        max_storage_mb: Optional[int] = None
    ) -> bool:
        """Update tenant limits."""
        try:
            tenant_model = self.session.query(TenantModel).filter(
                TenantModel.id == tenant_id
            ).first()
            if not tenant_model:
                return False
            
            if max_users is not None:
                tenant_model.max_users = max_users
            if max_calls_per_month is not None:
                tenant_model.max_calls_per_month = max_calls_per_month
            if max_storage_mb is not None:
                tenant_model.max_storage_mb = max_storage_mb
            
            tenant_model.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to update tenant limits: {e}")
