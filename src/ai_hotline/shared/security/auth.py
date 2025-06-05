"""Authentication and authorization utilities."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
from jose import jwt
from pydantic import BaseModel

from ..config.settings import get_settings


class TokenData(BaseModel):
    """Token data structure."""
    
    user_id: str
    username: str
    tenant_id: str
    email: str
    roles: list[str]
    exp: datetime
    iat: datetime
    jti: str


class PasswordManager:
    """Password hashing and verification manager."""
    
    def __init__(self):
        """Initialize password manager."""
        self.rounds = 12
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password to verify against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
    
    def generate_random_password(self, length: int = 12) -> str:
        """Generate a cryptographically secure random password.
        
        Args:
            length: Length of the password to generate
            
        Returns:
            Random password string
        """
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class TokenManager:
    """JWT token management."""
    
    def __init__(self):
        """Initialize token manager."""
        self.settings = get_settings()
        self.secret_key = self.settings.security.secret_key
        self.algorithm = self.settings.security.algorithm
        self.access_token_expire_minutes = self.settings.security.access_token_expire_minutes
        self.refresh_token_expire_days = self.settings.security.refresh_token_expire_days
    
    def create_access_token(
        self,
        user_id: str,
        username: str,
        tenant_id: str,
        email: str,
        roles: list[str],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create an access token.
        
        Args:
            user_id: User identifier
            username: Username
            tenant_id: Tenant identifier
            email: User email
            roles: User roles
            expires_delta: Optional expiration time override
            
        Returns:
            Encoded JWT token
        """
        now = datetime.now(timezone.utc)
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "username": username,
            "tenant_id": tenant_id,
            "email": email,
            "roles": roles,
            "exp": expire,
            "iat": now,
            "jti": secrets.token_urlsafe(16),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(
        self,
        user_id: str,
        tenant_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a refresh token.
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            expires_delta: Optional expiration time override
            
        Returns:
            Encoded JWT token
        """
        now = datetime.now(timezone.utc)
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "exp": expire,
            "iat": now,
            "jti": secrets.token_urlsafe(16),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Token payload
            
        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and extract data from a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            TokenData if valid, None if invalid
        """
        try:
            payload = self.decode_token(token)
            
            # Check token type
            if payload.get("type") != "access":
                return None
            
            # Extract token data
            return TokenData(
                user_id=payload["sub"],
                username=payload["username"],
                tenant_id=payload["tenant_id"],
                email=payload["email"],
                roles=payload["roles"],
                exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                iat=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
                jti=payload["jti"]
            )
        except (jwt.InvalidTokenError, KeyError, ValueError):
            return None
    
    def is_token_blacklisted(self, jti: str) -> bool:
        """Check if a token is blacklisted.
        
        Args:
            jti: Token JTI (unique identifier)
            
        Returns:
            True if blacklisted, False otherwise
            
        Note:
            This is a placeholder implementation.
            In production, you would check against a Redis cache or database.
        """
        # TODO: Implement token blacklist using Redis
        return False
    
    def blacklist_token(self, jti: str, exp: datetime) -> None:
        """Add a token to the blacklist.
        
        Args:
            jti: Token JTI (unique identifier)
            exp: Token expiration time
            
        Note:
            This is a placeholder implementation.
            In production, you would store in Redis cache with TTL.
        """
        # TODO: Implement token blacklist using Redis
        pass


# Global instances
password_manager = PasswordManager()
token_manager = TokenManager()
