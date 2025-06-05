"""Value objects for identity domain."""

import re
from typing import Any
from dataclasses import dataclass

from src.ai_hotline.shared.exceptions import ValidationError


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""
    
    value: str
    
    def __post_init__(self):
        """Validate email format."""
        if not self.value:
            raise ValidationError("Email cannot be empty")
        
        # Basic email validation
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        if not email_pattern.match(self.value):
            raise ValidationError("Invalid email format")
        
        if len(self.value) > 255:
            raise ValidationError("Email too long (max 255 characters)")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Username:
    """Username value object with validation."""
    
    value: str
    
    def __post_init__(self):
        """Validate username format."""
        if not self.value:
            raise ValidationError("Username cannot be empty")
        
        if len(self.value) < 3:
            raise ValidationError("Username must be at least 3 characters")
        
        if len(self.value) > 50:
            raise ValidationError("Username too long (max 50 characters)")
        
        # Allow alphanumeric, underscore, and dash
        username_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
        
        if not username_pattern.match(self.value):
            raise ValidationError(
                "Username can only contain letters, numbers, underscore, and dash"
            )
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Password:
    """Password value object with strength validation."""
    
    value: str
    
    def __post_init__(self):
        """Validate password strength."""
        if not self.value:
            raise ValidationError("Password cannot be empty")
        
        if len(self.value) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        if len(self.value) > 128:
            raise ValidationError("Password too long (max 128 characters)")
        
        # Check for basic strength requirements
        has_upper = any(c.isupper() for c in self.value)
        has_lower = any(c.islower() for c in self.value)
        has_digit = any(c.isdigit() for c in self.value)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in self.value)
        
        strength_checks = [has_upper, has_lower, has_digit, has_special]
        
        if sum(strength_checks) < 3:
            raise ValidationError(
                "Password must contain at least 3 of: uppercase, lowercase, digit, special character"
            )
    
    def __str__(self) -> str:
        return "*" * len(self.value)  # Never expose actual password


@dataclass(frozen=True)
class PhoneNumber:
    """Phone number value object with validation."""
    
    value: str
    
    def __post_init__(self):
        """Validate phone number format."""
        if not self.value:
            raise ValidationError("Phone number cannot be empty")
        
        # Remove common formatting
        cleaned = re.sub(r'[^\d+]', '', self.value)
        
        if not cleaned:
            raise ValidationError("Invalid phone number format")
        
        # Basic international format validation
        if not re.match(r'^\+?[1-9]\d{7,14}$', cleaned):
            raise ValidationError("Invalid phone number format")
        
        # Store the cleaned version
        object.__setattr__(self, 'value', cleaned)
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def formatted(self) -> str:
        """Get formatted phone number."""
        if self.value.startswith('+'):
            return self.value
        return f"+{self.value}"


@dataclass(frozen=True)
class TenantName:
    """Tenant name value object with validation."""
    
    value: str
    
    def __post_init__(self):
        """Validate tenant name."""
        if not self.value:
            raise ValidationError("Tenant name cannot be empty")
        
        if len(self.value) < 2:
            raise ValidationError("Tenant name must be at least 2 characters")
        
        if len(self.value) > 100:
            raise ValidationError("Tenant name too long (max 100 characters)")
        
        # Allow letters, numbers, spaces, and basic punctuation
        if not re.match(r'^[a-zA-Z0-9\s\-_.&()]+$', self.value):
            raise ValidationError(
                "Tenant name contains invalid characters"
            )
    
    def __str__(self) -> str:
        return self.value
