"""Mappers between domain entities and SQLAlchemy models."""

from typing import Optional
from uuid import UUID

from src.ai_hotline.modules.identity.domain.entities.user import User, UserRole
from src.ai_hotline.modules.identity.domain.value_objects import Email, Username, Password, PhoneNumber, TenantName
from ..persistence.models import UserModel, TenantModel


class UserMapper:
    """Mapper for User entity and UserModel."""
    
    @staticmethod
    def to_domain(model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        if not model:
            return None
        
        user = User(
            user_id=model.id,
            tenant_id=model.tenant_id,
            email=Email(model.email),
            username=Username(model.username),
            full_name=model.full_name,
            phone_number=PhoneNumber(model.phone_number) if model.phone_number else None,
            role=UserRole(model.role),
            is_active=model.is_active,
            is_email_verified=model.is_email_verified,
        )
        
        # Set additional attributes
        user._password_hash = model.password_hash
        user._failed_login_attempts = model.failed_login_attempts
        user._locked_until = model.locked_until
        user._last_login_at = model.last_login_at
        user._password_changed_at = model.password_changed_at
        user._avatar_url = model.avatar_url
        user._timezone = model.timezone
        user._language = model.language
        user.created_at = model.created_at
        user.updated_at = model.updated_at
        
        return user
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        """Convert domain entity to SQLAlchemy model."""
        if not entity:
            return None
        
        model = UserModel(
            id=entity.id,
            tenant_id=entity.tenant_id,
            email=entity.email.value,
            username=entity.username.value,
            full_name=entity.full_name,
            phone_number=entity.phone_number.value if entity.phone_number else None,
            password_hash=entity._password_hash,
            is_active=entity.is_active,
            is_email_verified=entity.is_email_verified,
            role=entity.role.value,
            failed_login_attempts=entity._failed_login_attempts,
            locked_until=entity._locked_until,
            last_login_at=entity._last_login_at,
            password_changed_at=entity._password_changed_at,
            avatar_url=entity._avatar_url,
            timezone=entity._timezone,
            language=entity._language,
        )
        
        # Set timestamps if they exist
        if hasattr(entity, 'created_at'):
            model.created_at = entity.created_at
        if hasattr(entity, 'updated_at'):
            model.updated_at = entity.updated_at
        
        return model
    
    @staticmethod
    def update_model_from_entity(model: UserModel, entity: User) -> UserModel:
        """Update SQLAlchemy model from domain entity."""
        model.email = entity.email.value
        model.username = entity.username.value
        model.full_name = entity.full_name
        model.phone_number = entity.phone_number.value if entity.phone_number else None
        model.password_hash = entity._password_hash
        model.is_active = entity.is_active
        model.is_email_verified = entity.is_email_verified
        model.role = entity.role.value
        model.failed_login_attempts = entity._failed_login_attempts
        model.locked_until = entity._locked_until
        model.last_login_at = entity._last_login_at
        model.password_changed_at = entity._password_changed_at
        model.avatar_url = entity._avatar_url
        model.timezone = entity._timezone
        model.language = entity._language
        
        return model


# TenantMapper temporarily removed due to architectural refactoring needs
