"""SQLAlchemy models for identity module."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from src.ai_hotline.shared.database.models import BaseModel, TenantBaseModel


class TenantModel(BaseModel):
    """SQLAlchemy model for Tenant entity."""
    
    __tablename__ = "tenants"
    
    # Identity
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Basic info
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Contact info
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    
    # Status and limits
    status = Column(String(20), nullable=False, default="trial")
    max_users = Column(Integer, nullable=False, default=5)
    max_calls_per_month = Column(Integer, nullable=False, default=100)
    max_storage_mb = Column(Integer, nullable=False, default=1000)
    
    # Features and settings
    features = Column(JSON, nullable=False, default=dict)
    settings = Column(JSON, nullable=False, default=dict)
    
    # Trial info
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Relationships
    users = relationship(
        "UserModel", 
        back_populates="tenant", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<TenantModel(id={self.id}, name={self.name}, status={self.status})>"


class UserModel(TenantBaseModel):
    """SQLAlchemy model for User entity."""
    
    __tablename__ = "users" 
    
    # Basic info
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    
    # Role and permissions
    role = Column(String(50), nullable=False, default="OPERATOR")
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Role and status
    role = Column(String(20), nullable=False, default="viewer")
    status = Column(String(20), nullable=False, default="pending_verification")
    
    # Verification flags
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    
    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    bio = Column(Text, nullable=True)
    
    # Relationships
    
    # Tenant relationship
    tenant_id = Column(
        PostgresUUID(as_uuid=True), 
        ForeignKey("tenants.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    tenant = relationship(
        "TenantModel", 
        back_populates="users",
        lazy="joined"  # Eager loading for tenant
    )

    preferences = relationship(
        "UserPreferencesModel", 
        back_populates="user",
        uselist=False,  # One-to-one relationship
        cascade="all, delete-orphan",
        lazy="select"
    )

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"


class UserPreferencesModel(TenantBaseModel):
    """SQLAlchemy model for User Preferences."""
    
    __tablename__ = "user_preferences"
    
    # Foreign key to user
    user_id = Column(
        PostgresUUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        unique=True,  # Ensure one-to-one relationship
        index=True
    )
    
    # UI Preferences
    theme = Column(String(20), default="light", nullable=False)  # light, dark, auto
    language_ui = Column(String(10), default="en", nullable=False)  # UI language
    sidebar_collapsed = Column(Boolean, default=False, nullable=False)
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)
    
    # Call Processing Preferences
    auto_answer_calls = Column(Boolean, default=False, nullable=False)
    preferred_tts_voice = Column(String(50), default="default", nullable=False)
    preferred_stt_model = Column(String(50), default="munsit-1", nullable=False)
    max_call_duration = Column(Integer, default=1800, nullable=False)  # 30 minutes
    
    # Dashboard Preferences
    default_dashboard_view = Column(String(50), default="overview", nullable=False)
    items_per_page = Column(Integer, default=25, nullable=False)
    
    # Additional settings as JSON
    custom_settings = Column(Text, nullable=True)  # JSON string for flexible settings
    
    # Relationships
    user = relationship(
        "UserModel", 
        back_populates="preferences",
        lazy="joined"
    )
    
    def __repr__(self):
        return f"<UserPreferencesModel(user_id={self.user_id}, theme={self.theme})>"
