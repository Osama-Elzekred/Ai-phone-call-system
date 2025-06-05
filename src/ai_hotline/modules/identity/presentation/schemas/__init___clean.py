"""Pydantic schemas for identity API."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from ..domain.entities.user import UserRole, UserStatus


class UserLoginRequest(BaseModel):
    """User login request schema."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class TokenResponse(BaseModel):
    """Token response schema."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token") 
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    
    refresh_token: str = Field(..., description="Refresh token")


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Check for basic strength requirements
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        strength_checks = [has_upper, has_lower, has_digit, has_special]
        
        if sum(strength_checks) < 3:
            raise ValueError(
                "Password must contain at least 3 of: uppercase, lowercase, digit, special character"
            )
        
        return v


class UserCreateRequest(BaseModel):
    """User creation request schema."""
    
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                "Username can only contain letters, numbers, underscore, and dash"
            )
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Check for basic strength requirements
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        strength_checks = [has_upper, has_lower, has_digit, has_special]
        
        if sum(strength_checks) < 3:
            raise ValueError(
                "Password must contain at least 3 of: uppercase, lowercase, digit, special character"
            )
        
        return v


class UserUpdateRequest(BaseModel):
    """User update request schema."""
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Last name")
    role: Optional[UserRole] = Field(None, description="User role")


class UserResponse(BaseModel):
    """User response schema."""
    
    id: UUID = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., description="Username")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(..., description="User status")
    email_verified: bool = Field(..., description="Email verification status")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """User list response schema."""
    
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")


class TenantCreateRequest(BaseModel):
    """Tenant creation request schema."""
    
    name: str = Field(..., min_length=2, max_length=100, description="Tenant name")
    display_name: str = Field(..., min_length=2, max_length=200, description="Display name")
    description: Optional[str] = Field(None, max_length=500, description="Tenant description")
    contact_email: EmailStr = Field(..., description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    
    @field_validator("name")
    @classmethod
    def validate_tenant_name(cls, v):
        """Validate tenant name format."""
        if not re.match(r'^[a-zA-Z0-9\s\-_.&()]+$', v):
            raise ValueError("Tenant name contains invalid characters")
        return v


class TenantResponse(BaseModel):
    """Tenant response schema."""
    
    id: UUID = Field(..., description="Tenant ID")
    name: str = Field(..., description="Tenant name")
    display_name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Description")
    contact_email: EmailStr = Field(..., description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    status: str = Field(..., description="Tenant status")
    max_users: int = Field(..., description="Maximum users allowed")
    max_calls_per_month: int = Field(..., description="Maximum calls per month")
    max_storage_mb: int = Field(..., description="Maximum storage in MB")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: dict = Field(default_factory=dict, description="Additional error details")
