"""Mappers between domain entities and SQLAlchemy models."""

from typing import Optional
from uuid import UUID

from src.ai_hotline.modules.identity.domain.entities.user import User, UserRole
from src.ai_hotline.modules.identity.domain.entities.tenant import Tenant
from ..persistence.models import UserModel, TenantModel


class UserMapper:
    """Mapper for User entity and UserModel."""
    
    @staticmethod
    def to_domain(model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        if not model:
            return None
        
        return User(
            id=model.id,
            tenant_id=model.tenant_id,
            email=model.email,
            username=model.username,
            password_hash=model.password_hash,
            first_name=model.first_name,
            last_name=model.last_name,
            role=model.role,
            status=model.status,
            email_verified=model.email_verified,
            phone_verified=model.phone_verified,
            last_login=model.last_login_at,
            failed_login_attempts=model.failed_login_attempts,
            locked_until=model.locked_until,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Convert domain entity to SQLAlchemy model."""
        if not entity:
            return None
        
        model = UserModel(
            id=entity.id,
            tenant_id=entity.tenant_id,
            email=entity.email,
            username=entity.username,
            password_hash=entity.password_hash,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role,
            status=entity.status,
            email_verified=entity.email_verified,
            phone_verified=entity.phone_verified,
            last_login_at=entity.last_login_at,
            failed_login_attempts=entity.failed_login_attempts,
            locked_until=entity.locked_until,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            )
        
        return model
    
    @staticmethod
    def update_model_from_entity(model: UserModel, entity: User) -> UserModel:
        """Update SQLAlchemy model from domain entity."""
        model.email = entity.email
        model.username = entity.username
        model.password_hash = entity.password_hash
        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.role = entity.role
        model.status = entity.status
        model.email_verified = entity.email_verified
        model.phone_verified = entity.phone_verified
        model.last_login_at = entity.last_login_at
        model.failed_login_attempts = entity.failed_login_attempts
        model.locked_until = entity.locked_until
        model.updated_at = entity.updated_at
        
        return model


class TenantMapper:
    """Mapper for Tenant entity and TenantModel."""
    
    @staticmethod
    def to_domain(model: TenantModel) -> Tenant:
        """Convert SQLAlchemy model to domain entity."""
        if not model:
            return None
        
        import json
        
        # Parse JSON strings to dictionaries if they exist
        features = json.loads(model.features) if model.features else {}
        settings = json.loads(model.settings) if model.settings else {}

        return Tenant(
            id=model.id,
            name=model.name,
            display_name=model.display_name,
            description=model.description,
            contact_email=model.contact_email,
            contact_phone=model.contact_phone,
            status=model.status,
            max_users=model.max_users,
            max_calls_per_month=model.max_calls_per_month,
            max_storage_mb=model.max_storage_mb,
            features=features or {},
            settings=settings or {},
            trial_ends_at=model.trial_ends_at,            
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    @staticmethod
    def to_model(entity: Tenant) -> TenantModel:
        """Convert domain entity to SQLAlchemy model."""
        if not entity:
            return None
        
        import json
        
        return TenantModel(
            id=entity.id,
            name=entity.name,
            display_name=entity.display_name,
            description=entity.description,
            contact_email=entity.contact_email,
            contact_phone=entity.contact_phone,
            status=entity.status,
            max_users=entity.max_users,
            max_calls_per_month=entity.max_calls_per_month,            
            max_storage_mb=entity.max_storage_mb,
            features=json.dumps(entity.features) if entity.features else None,
            settings=json.dumps(entity.settings) if entity.settings else None,
            trial_ends_at=entity.trial_ends_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def update_model_from_entity(model: TenantModel, entity: Tenant) -> TenantModel:
        """Update SQLAlchemy model from domain entity."""
        model.name = entity.name
        model.display_name = entity.display_name
        model.description = entity.description
        model.contact_email = entity.contact_email
        model.contact_phone = entity.contact_phone
        model.status = entity.status
        model.max_users = entity.max_users
        model.max_calls_per_month = entity.max_calls_per_month
        model.max_storage_mb = entity.max_storage_mb
        model.features = entity.features
        model.settings = entity.settings
        model.trial_ends_at = entity.trial_ends_at
        model.updated_at = entity.updated_at
        
        return model
