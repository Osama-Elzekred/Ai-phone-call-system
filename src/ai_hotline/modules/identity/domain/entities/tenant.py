"""Tenant domain entity."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from enum import Enum

from src.ai_hotline.shared.exceptions import BusinessRuleViolationError


class TenantStatus(str, Enum):
    """Tenant status constants."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class Tenant(BaseModel):
    """
    Tenant entity for multi-tenancy support.
    
    Domain Rules:
    - Tenant name must be unique
    - Active tenants can have users and process calls
    - Suspended tenants cannot process new calls
    - Trial tenants have usage limitations
    """
    
    # Identity
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Basic info
    name: str
    display_name: str
    description: Optional[str] = None
    
    # Contact info
    contact_email: str
    contact_phone: Optional[str] = None
      # Status and limits
    status: str = TenantStatus.TRIAL.value
    max_users: int = 5
    max_calls_per_month: int = 100
    max_storage_mb: int = 1000  # 1GB
    
    # Features and settings
    features: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    # Trial info
    trial_ends_at: Optional[str] = None  # ISO date string
    
    def __init__(self, name: str, display_name: str, contact_email: str, **kwargs):
        """Initialize tenant with required fields."""
        super().__init__(
            name=name,
            display_name=display_name,
            contact_email=contact_email,
            **kwargs
        )
        
        # Set default features if not provided
        if not self.features:
            self.features = {
                "stt_enabled": True,
                "tts_enabled": True,
                "llm_providers": ["openai"],
                "knowledge_management": True,
                "automation": False,
                "analytics": True,
                "api_access": False
            }
        
        # Set default settings if not provided
        if not self.settings:
            self.settings = {
                "default_language": "ar-EG",  # Egyptian Arabic
                "default_voice": "arabic_female_1",
                "call_timeout_seconds": 300,
                "max_call_duration_minutes": 30,                "auto_transcription": True,
                "data_retention_days": 365
            }

    @property
    def is_active_tenant(self) -> bool:
        """Check if tenant is active."""
        return self.status == TenantStatus.ACTIVE.value
    
    @property
    def is_trial(self) -> bool:
        """Check if tenant is on trial."""
        return self.status == TenantStatus.TRIAL.value
    
    @property
    def is_suspended(self) -> bool:
        """Check if tenant is suspended."""
        return self.status == TenantStatus.SUSPENDED.value
    
    def activate(self) -> None:
        """Activate tenant."""
        if self.status == TenantStatus.EXPIRED.value:
            raise BusinessRuleViolationError("Cannot activate expired tenant")
        
        self.status = TenantStatus.ACTIVE.value
    
    def suspend(self) -> None:
        """Suspend tenant."""
        self.status = TenantStatus.SUSPENDED.value
    
    def expire_trial(self) -> None:
        """Mark trial as expired."""
        if not self.is_trial:
            raise BusinessRuleViolationError("Cannot expire non-trial tenant")
        
        self.status = TenantStatus.EXPIRED.value

    def upgrade_from_trial(self) -> None:
        """Upgrade from trial to active."""
        if not self.is_trial:
            raise BusinessRuleViolationError("Can only upgrade trial tenants")
        
        self.status = TenantStatus.ACTIVE.value
        self.trial_ends_at = None
    
    def update_limits(
        self,
        max_users: Optional[int] = None,
        max_calls_per_month: Optional[int] = None,
        max_storage_mb: Optional[int] = None
    ) -> None:
        """Update tenant limits."""
        if max_users is not None:
            if max_users < 1:
                raise BusinessRuleViolationError("Max users must be at least 1")
            self.max_users = max_users
        
        if max_calls_per_month is not None:
            if max_calls_per_month < 0:
                raise BusinessRuleViolationError("Max calls cannot be negative")
            self.max_calls_per_month = max_calls_per_month
        
        if max_storage_mb is not None:
            if max_storage_mb < 0:
                raise BusinessRuleViolationError("Max storage cannot be negative")
            self.max_storage_mb = max_storage_mb
    
    def enable_feature(self, feature_name: str) -> None:
        """Enable a feature for the tenant."""
        if not self.features:
            self.features = {}
        
        self.features[feature_name] = True
    
    def disable_feature(self, feature_name: str) -> None:
        """Disable a feature for the tenant."""
        if not self.features:
            self.features = {}
        
        self.features[feature_name] = False
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if tenant has a specific feature enabled."""
        if not self.features:
            return False
        
        return self.features.get(feature_name, False)
    
    def update_setting(self, setting_name: str, value: Any) -> None:
        """Update a tenant setting."""
        if not self.settings:
            self.settings = {}
        
        self.settings[setting_name] = value
    
    def get_setting(self, setting_name: str, default: Any = None) -> Any:
        """Get a tenant setting value."""
        if not self.settings:
            return default
        
        return self.settings.get(setting_name, default)
    
    def can_create_user(self, current_user_count: int) -> bool:
        """Check if tenant can create another user."""
        if not self.is_active_tenant:
            return False
        
        return current_user_count < self.max_users
    
    def can_process_call(self, current_monthly_calls: int) -> bool:
        """Check if tenant can process another call this month."""
        if not self.is_active_tenant:
            return False
        
        return current_monthly_calls < self.max_calls_per_month
    
    def __str__(self) -> str:
        """String representation."""
        return f"Tenant({self.name}, {self.status})"
