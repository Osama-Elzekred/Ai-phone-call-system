"""SQLAlchemy models for identity module."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from src.ai_hotline.shared.database.models import BaseModel, TenantBaseModel


class TenantModel(BaseModel):
    """SQLAlchemy model for Tenant entity."""
    
    __tablename__ = "tenants_persistence"
    
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True, nullable=False)
    max_users = Column(Integer, default=100, nullable=False)
    max_calls_per_month = Column(Integer, default=1000, nullable=False)
    
    # Feature flags
    features_stt_enabled = Column(Boolean, default=True, nullable=False)
    features_tts_enabled = Column(Boolean, default=True, nullable=False)
    features_llm_enabled = Column(Boolean, default=True, nullable=False)
    features_automation_enabled = Column(Boolean, default=False, nullable=False)
    features_knowledge_base_enabled = Column(Boolean, default=False, nullable=False)
    
    # Subscription info
    subscription_plan = Column(String(50), default="basic", nullable=False)
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    users = relationship("UserModel", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TenantModel(id={self.id}, name={self.name}, is_active={self.is_active})>"


class UserModel(TenantBaseModel):
    """SQLAlchemy model for User entity."""
    
    __tablename__ = "users_persistence"
    
    # Basic info
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    
    # Role and permissions
    role = Column(String(50), nullable=False, default="OPERATOR")
    
    # Security
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
      # Profile
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="ar", nullable=False)
    bio = Column(Text, nullable=True)  # New column for user biography
    
    # Relationships
    tenant = relationship("TenantModel", back_populates="users")
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"


class UserPreferencesModel(TenantBaseModel):
    """SQLAlchemy model for User Preferences."""
    
    __tablename__ = "user_preferences"
    
    # Foreign key to user
    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey('users_persistence.id'), nullable=False)
    
    # UI Preferences
    theme = Column(String(20), default="light", nullable=False)  # light, dark, auto
    language_ui = Column(String(10), default="ar", nullable=False)  # UI language
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
    user = relationship("UserModel", backref="preferences")
    
    def __repr__(self):
        return f"<UserPreferencesModel(user_id={self.user_id}, theme={self.theme})>"
