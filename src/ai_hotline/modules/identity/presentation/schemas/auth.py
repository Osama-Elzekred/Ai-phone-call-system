"""Pydantic schemas for identity API."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.ai_hotline.modules.identity.domain.entities.user import UserRole, UserStatus
from src.ai_hotline.modules.identity.domain.entities.tenant import TenantStatus


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER
    tenant_id: UUID
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        strength_checks = [has_upper, has_lower, has_digit, has_special]
        
        if sum(strength_checks) < 3:
            raise ValueError(
                'Password must contain at least 3 of: uppercase, lowercase, digit, special character'
            )
        
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    tenant_id: UUID
    role: UserRole
    status: UserStatus
    email_verified: bool
    phone_verified: bool
    last_login: Optional[datetime]
    failed_login_attempts: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserList(BaseModel):
    """Schema for user list response."""
    users: list[UserResponse]
    total: int
    page: int
    size: int


# Authentication Schemas
class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Schema for token refresh response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        strength_checks = [has_upper, has_lower, has_digit, has_special]
        
        if sum(strength_checks) < 3:
            raise ValueError(
                'Password must contain at least 3 of: uppercase, lowercase, digit, special character'
            )
        
        return v


# Tenant Schemas
class TenantBase(BaseModel):
    """Base tenant schema."""
    name: str = Field(..., min_length=2, max_length=100)
    display_name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    contact_email: EmailStr
    contact_phone: Optional[str] = None


class TenantCreate(TenantBase):
    """Schema for tenant creation."""
    max_users: int = Field(5, ge=1)
    max_calls_per_month: int = Field(100, ge=0)
    max_storage_mb: int = Field(1000, ge=0)


class TenantUpdate(BaseModel):
    """Schema for tenant updates."""
    display_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    status: Optional[TenantStatus] = None
    max_users: Optional[int] = Field(None, ge=1)
    max_calls_per_month: Optional[int] = Field(None, ge=0)
    max_storage_mb: Optional[int] = Field(None, ge=0)


class TenantResponse(TenantBase):
    """Schema for tenant response."""
    id: UUID
    status: TenantStatus
    max_users: int
    max_calls_per_month: int
    max_storage_mb: int
    features: dict
    settings: dict
    trial_ends_at: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantList(BaseModel):
    """Schema for tenant list response."""
    tenants: list[TenantResponse]
    total: int
    page: int
    size: int


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    message: str
    details: Optional[dict] = None
