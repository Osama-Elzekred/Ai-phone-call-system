"""SQLAlchemy implementation of user repository."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.ai_hotline.shared.exceptions import DatabaseError, EntityNotFoundError
from src.ai_hotline.modules.identity.domain.entities.user import User
from src.ai_hotline.modules.identity.domain.repositories import IUserRepository
from ..persistence.models import UserModel
from ..mappers.user_mapper import UserMapper


class SqlAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        try:
            user_model = UserMapper.to_model(user)
            self.session.add(user_model)
            self.session.commit()
            self.session.refresh(user_model)
            return UserMapper.to_domain(user_model)
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to create user: {e}")
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            user_model = self.session.query(UserModel).filter(
                and_(UserModel.id == user_id, UserModel.is_active == True)
            ).first()
            return UserMapper.to_domain(user_model) if user_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get user by ID: {e}")
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            user_model = self.session.query(UserModel).filter(
                and_(UserModel.email == email, UserModel.is_active == True)
            ).first()
            return UserMapper.to_domain(user_model) if user_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get user by email: {e}")
    
    async def get_by_username(self, username: str, tenant_id: UUID) -> Optional[User]:
        """Get user by username within tenant."""
        try:
            user_model = self.session.query(UserModel).filter(
                and_(
                    UserModel.username == username,
                    UserModel.tenant_id == tenant_id,
                    UserModel.is_active == True
                )
            ).first()
            return UserMapper.to_domain(user_model) if user_model else None
        except Exception as e:
            raise DatabaseError(f"Failed to get user by username: {e}")
    
    async def update(self, user: User) -> User:
        """Update user."""
        try:
            # Get existing model
            existing_model = self.session.query(UserModel).filter(UserModel.id == user.id).first()
            if not existing_model:
                raise EntityNotFoundError("User not found")
            
            # Update model from entity
            UserMapper.update_model_from_entity(existing_model, user)
            self.session.commit()
            self.session.refresh(existing_model)
            return UserMapper.to_domain(existing_model)
        except EntityNotFoundError:
            raise
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to update user: {e}")
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user (soft delete)."""
        try:
            user_model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
            if not user_model:
                return False
            
            user_model.soft_delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to delete user: {e}")
    
    async def list_by_tenant(
        self, 
        tenant_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """List users in a tenant."""
        try:
            user_models = self.session.query(UserModel).filter(
                and_(
                    UserModel.tenant_id == tenant_id,
                    UserModel.is_active == True
                )
            ).offset(skip).limit(limit).all()
            return [UserMapper.to_domain(model) for model in user_models]
        except Exception as e:
            raise DatabaseError(f"Failed to list users by tenant: {e}")
    
    async def count_by_tenant(self, tenant_id: UUID) -> int:
        """Count users in a tenant."""
        try:
            return self.session.query(UserModel).filter(
                and_(
                    UserModel.tenant_id == tenant_id,
                    UserModel.is_active == True
                )
            ).count()
        except Exception as e:
            raise DatabaseError(f"Failed to count users by tenant: {e}")
    
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        try:
            count = self.session.query(UserModel).filter(
                and_(UserModel.email == email, UserModel.is_active == True)
            ).count()
            return count > 0
        except Exception as e:
            raise DatabaseError(f"Failed to check email existence: {e}")
    
    async def username_exists(self, username: str, tenant_id: UUID) -> bool:
        """Check if username exists in tenant."""
        try:
            count = self.session.query(UserModel).filter(
                and_(
                    UserModel.username == username,
                    UserModel.tenant_id == tenant_id,
                    UserModel.is_active == True
                )
            ).count()
            return count > 0
        except Exception as e:
            raise DatabaseError(f"Failed to check username existence: {e}")
