"""Authentication service for identity module."""

from datetime import datetime
from typing import Optional, Tuple
from pydantic import EmailStr
from uuid import UUID
import logging

from src.ai_hotline.shared.security.auth import token_manager, password_manager
from src.ai_hotline.shared.exceptions import (
    AuthenticationError,
    EntityNotFoundError,
    BusinessRuleViolationError
)
from src.ai_hotline.modules.identity.domain.entities.user import User, UserStatus, UserRole
from src.ai_hotline.modules.identity.domain.entities.tenant import Tenant
from src.ai_hotline.modules.identity.domain.repositories import IUserRepository, ITenantRepository


class AuthenticationService:
    """Service for user authentication operations."""
    
    def __init__(self, user_repository: IUserRepository, tenant_repository: ITenantRepository):
        self.user_repository = user_repository
        self.tenant_repository = tenant_repository  
        self.logger = logging.getLogger(__name__)
    
    async def register_tenant_with_admin(
        self,
        tenant_name: str,
        tenant_display_name: str,
        admin_email: EmailStr,
        admin_password: str,
        admin_username: str,
    ) -> Tuple[Tenant, User, str, str]:
        """
        Create a new tenant and its first admin user atomically.
        
        Args:
            tenant_name: Unique tenant identifier
            tenant_display_name: Display name for tenant
            admin_email: Email for tenant admin
            admin_password: Password for tenant admin
            admin_username: Username for tenant admin
            current_user: Optional current user (must be super admin if provided)
            
        Returns:
            Tuple of (tenant, admin_user, access_token, refresh_token)
            
        Raises:
            BusinessRuleViolationError: If tenant exists or permission denied
        """
        # # Check permissions if current user provided
        # if current_user and current_user.role != UserRole.SUPER_ADMIN:
        #     raise BusinessRuleViolationError("Only super admins can create tenants")

        try:
            # Check if tenant already exists
            existing_tenant = await self.tenant_repository.get_by_name(tenant_name)
            if existing_tenant:
                self.logger.warning(f"Tenant registration failed: tenant already exists with name {tenant_name}")
                raise BusinessRuleViolationError(f"Tenant with name '{tenant_name}' already exists")
    
            # Check if admin email is already in use
            existing_user = await self.user_repository.get_by_email(admin_email)
            if existing_user:
                self.logger.warning(f"Tenant registration failed: admin email already in use {admin_email}")
                raise BusinessRuleViolationError("Admin email is already in use")
    
            # Create tenant
            tenant = Tenant(
                name=tenant_name,
                display_name=tenant_display_name,
                contact_email=admin_email,
            )
            created_tenant = await self.tenant_repository.create(tenant)
            
            try:
                # Create admin user
                user, access_token, refresh_token = await self.register_tenant_user(
                    email=admin_email,
                    password=admin_password,
                    username=admin_username,
                    role=UserRole.TENANT_ADMIN,
                    tenant_id=created_tenant.id
                )
                
                self.logger.info(f"Successfully created tenant '{tenant_name}' with admin user")
                return created_tenant, user, access_token, refresh_token
                
            except Exception as user_error:
                # If user creation fails, clean up the tenant
                self.logger.error(f"Failed to create admin user, cleaning up tenant: {str(user_error)}")
                await self.tenant_repository.delete(created_tenant.id)
                raise BusinessRuleViolationError("Failed to create tenant admin user") from user_error
                
        except Exception as e:
            self.logger.error(f"Tenant registration failed: {str(e)}")
            raise BusinessRuleViolationError("Failed to register tenant and admin") from e


    async def register_tenant_user(
        self,
        email: EmailStr,
        password: str,
        username: Optional[str] = None,
        role: UserRole = UserRole.VIEWER,
        tenant_id: Optional[UUID] = None
    ) -> Tuple[User, str, str]:
        """
        Register a new user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            username: Optional username
            role: User role (default is 'user')
            tenant_id: Optional tenant ID
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            BusinessRuleViolationError: If user already exists
        """
        try:
            # Check if user already exists
            existing_user = await self.user_repository.get_by_email(email.__str__())
            if existing_user:
                self.logger.warning(f"User registration failed: user already exists for email {email.__str__()}")
                raise BusinessRuleViolationError("User already exists")
            
            # Hash password
            password_hash = password_manager.hash_password(password)
            
            # Create new user entity
            user = User(
                email=email,
                password_hash=password_hash,
                username=username,
                role=role,
                tenant_id=tenant_id,
                last_login_at=datetime.utcnow()
            )
            
            # Save user to repository
            await self.user_repository.create(user)
            
            # Generate tokens
            access_token = token_manager.create_access_token(
                user_id=str(user.id),
                username=user.username,
                tenant_id=user.tenant_id,
                email=user.email,
                roles=[role],
            )

            refresh_token = token_manager.create_refresh_token(
                user_id=str(user.id),
                tenant_id=user.tenant_id
            )
            
            self.logger.info(f"User registered successfully: {user.id}")
            return user, access_token, refresh_token
        except Exception as e:
            self.logger.error(f"User registration failed: {e}")
            raise BusinessRuleViolationError("Failed to register user")
    
    async def authenticate_user(
        self, 
        email: str, 
        password: str
    ) -> Tuple[User, str, str]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            self.logger.warning(f"Authentication failed: user not found for email {email}")
            raise AuthenticationError("Invalid email or password")
        
        # Check if account is locked
        if user.is_locked:
            self.logger.warning(f"Authentication failed: account locked for user {user.id}")
            raise AuthenticationError("Account is temporarily locked")
        
        # # Check if account is active
        # if not user.is_active_user:
        #     self.logger.warning(f"Authentication failed: inactive account for user {user.id}")
        #     raise AuthenticationError("Account is not active")
        
        # Verify password
        if not password_manager.verify_password(password, user.password_hash):
            # Record failed login attempt
            user.record_failed_login()
            await self.user_repository.update(user)
            
            self.logger.warning(f"Authentication failed: invalid password for user {user.id}")
            raise AuthenticationError("Invalid email or password")
        
        # # Check if password needs update
        # if password_manager.needs_update(user.password_hash):
        #     self.logger.info(f"Password hash needs update for user {user.id}")
        
        # Record successful login
        user.record_login()
        await self.user_repository.update(user)
        
        # Generate tokens
        access_token = token_manager.create_access_token(
            user_id=str(user.id),
            username=user.username,
            tenant_id=user.tenant_id,
            email=user.email,
            roles=[user.role],
        )
        
        refresh_token = token_manager.create_refresh_token(
            user_id=str(user.id),
            tenant_id=user.tenant_id
        )
        
        self.logger.info(f"User authenticated successfully: {user.id}")
        return user, access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            AuthenticationError: If refresh token is invalid
        """
        try:
            # Verify refresh token
            payload = token_manager.verify_token(refresh_token)
            
            # Check token type
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            
            user_id = UUID(payload["sub"])
            
            # Get user to ensure they still exist and are active
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise AuthenticationError("User not found")
            
            if not user.is_active_user:
                raise AuthenticationError("User account is not active")
            
            # Generate new access token
            access_token = token_manager.create_access_token(
                subject=str(user.id),
                tenant_id=user.tenant_id,
                additional_claims={
                    "role": user.role,
                    "email": user.email,
                    "username": user.username
                }
            )
            
            self.logger.info(f"Access token refreshed for user: {user.id}")
            return access_token
            
        except Exception as e:
            self.logger.warning(f"Token refresh failed: {e}")
            raise AuthenticationError("Invalid refresh token")
    
    async def verify_token_and_get_user(self, token: str) -> User:
        """
        Verify access token and return user.
        
        Args:
            token: Access token to verify
            
        Returns:
            User associated with the token
            
        Raises:
            AuthenticationError: If token is invalid or user not found
        """
        try:
            # Verify token
            payload = token_manager.verify_token(token)
            
            # Check token type
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")
            
            user_id = UUID(payload["sub"])
            
            # Get user
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise AuthenticationError("User not found")
            
            if not user.is_active_user:
                raise AuthenticationError("User account is not active")
            
            return user
            
        except Exception as e:
            self.logger.warning(f"Token verification failed: {e}")
            raise AuthenticationError("Invalid token")
    
    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Raises:
            AuthenticationError: If current password is wrong
            EntityNotFoundError: If user not found
        """
        # Get user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User not found")
        
        # Verify current password
        if not password_manager.verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        
        # Hash new password and update
        new_password_hash = password_manager.hash_password(new_password)
        user.change_password(new_password_hash)
        
        await self.user_repository.update(user)
        
        self.logger.info(f"Password changed for user: {user.id}")
    
    async def reset_password(self, email: str, new_password: str) -> None:
        """
        Reset user password (admin operation).
        
        Args:
            email: User email
            new_password: New password
            
        Raises:
            EntityNotFoundError: If user not found
        """
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise EntityNotFoundError("User not found")
        
        # Hash new password and update
        new_password_hash = password_manager.hash_password(new_password)
        user.change_password(new_password_hash)
        
        await self.user_repository.update(user)
        
        self.logger.info(f"Password reset for user: {user.id}")
    
    async def unlock_user_account(self, user_id: UUID) -> None:
        """
        Unlock a locked user account (admin operation).
        
        Args:
            user_id: User ID to unlock
            
        Raises:
            EntityNotFoundError: If user not found
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User not found")
        
        user.unlock_account()
        await self.user_repository.update(user)
        
        self.logger.info(f"Account unlocked for user: {user.id}")
