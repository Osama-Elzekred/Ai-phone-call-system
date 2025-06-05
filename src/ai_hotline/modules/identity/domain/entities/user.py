"""User domain entity."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field

from src.ai_hotline.shared.exceptions import BusinessRuleViolationError


class UserRole(str, Enum):
    """User roles in the system."""
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(BaseModel):
    """
    User entity representing system users.
    
    Domain Rules:
    - Email must be unique within the system
    - Username must be unique within tenant
    - Users must have at least one role
    - Super admins can access all tenants
    """
    
    # Identity
    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Basic info
    email: str
    username: str
    password_hash: str
    first_name: str
    last_name: str
    
    # Role and status
    role: str = UserRole.VIEWER.value
    status: str = UserStatus.PENDING_VERIFICATION.value
    
    # Verification flags
    email_verified: bool = False
    phone_verified: bool = False
    
    # Security tracking
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_active_user(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE.value
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def change_email(self, new_email: str) -> None:
        """Change user email and require re-verification."""
        if self.status == UserStatus.SUSPENDED.value:
            raise BusinessRuleViolationError("Cannot change email for suspended user")
        
        self.email = new_email
        self.email_verified = False
    
    def change_password(self, new_password_hash: str) -> None:
        """Change user password and reset security flags."""
        if self.status == UserStatus.SUSPENDED.value:
            raise BusinessRuleViolationError("Cannot change password for suspended user")
        
        self.password_hash = new_password_hash
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def change_role(self, new_role: UserRole) -> None:
        """Change user role."""
        if self.status == UserStatus.SUSPENDED.value:
            raise BusinessRuleViolationError("Cannot change role for suspended user")
        
        self.role = new_role.value
    
    def activate(self) -> None:
        """Activate user account."""
        if self.status == UserStatus.SUSPENDED.value:
            raise BusinessRuleViolationError("Cannot activate suspended user")
        
        self.status = UserStatus.ACTIVE.value
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.status = UserStatus.INACTIVE.value
    
    def suspend(self) -> None:
        """Suspend user account."""
        self.status = UserStatus.SUSPENDED.value
    
    def verify_email(self) -> None:
        """Mark email as verified and auto-activate if pending."""
        self.email_verified = True
        
        if self.status == UserStatus.PENDING_VERIFICATION.value:
            self.status = UserStatus.ACTIVE.value
    
    def record_login(self) -> None:
        """Record successful login."""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def record_failed_login(self, max_attempts: int = 5, lockout_minutes: int = 30) -> None:
        """Record failed login attempt and lock if needed."""
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= max_attempts:
            self.locked_until = datetime.utcnow().replace(
                minute=datetime.utcnow().minute + lockout_minutes
            )
    
    def unlock_account(self) -> None:
        """Unlock user account."""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def can_access_tenant(self, tenant_id: UUID) -> bool:
        """Check if user can access a specific tenant."""
        # Super admins can access all tenants
        if self.role == UserRole.SUPER_ADMIN.value:
            return True
        
        # Regular users can only access their own tenant
        return self.tenant_id == tenant_id
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission based on role."""
        permissions = {
            UserRole.SUPER_ADMIN.value: ["*"],  # All permissions
            UserRole.TENANT_ADMIN.value: [
                "users.create", "users.read", "users.update", "users.delete",
                "calls.read", "calls.manage", "knowledge.manage", "automation.manage"
            ],
            UserRole.OPERATOR.value: [
                "calls.read", "calls.create", "knowledge.read", "automation.execute"
            ],
            UserRole.VIEWER.value: [
                "calls.read", "knowledge.read"
            ]
        }
        
        user_permissions = permissions.get(self.role, [])
        
        # Super admin has all permissions
        if "*" in user_permissions:
            return True
        
        return permission in user_permissions
    
    def __str__(self) -> str:
        """String representation."""
        return f"User({self.username}, {self.email})"