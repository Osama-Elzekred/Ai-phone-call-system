"""Authentication middleware for request processing."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..security.auth import verify_access_token
from ..exceptions.exceptions import AuthenticationError, AuthorizationError
from ..logging import get_logger

logger = get_logger("auth.middleware")


class JWTBearer(HTTPBearer):
    """JWT Bearer token authentication."""
    
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[str]:
        """Extract and validate JWT token from request."""
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            
            return credentials.credentials
        else:
            return None
    
    def verify_jwt(self, jwt_token: str) -> bool:
        """Verify JWT token validity."""
        try:
            payload = verify_access_token(jwt_token)
            return payload is not None
        except AuthenticationError:
            return False


# Create instance for dependency injection
jwt_bearer = JWTBearer()


async def get_current_user_id(token: str = jwt_bearer) -> str:
    """Get current user ID from JWT token."""
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationError("Invalid token: missing user ID")
        
        return user_id
    
    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_tenant_id(token: str = jwt_bearer) -> str:
    """Get current tenant ID from JWT token."""
    try:
        payload = verify_access_token(token)
        tenant_id = payload.get("tenant_id")
        
        if tenant_id is None:
            raise AuthenticationError("Invalid token: missing tenant ID")
        
        return tenant_id
    
    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(required_role: str):
    """Decorator to require specific role for endpoint access."""
    async def role_checker(token: str = jwt_bearer) -> str:
        try:
            payload = verify_access_token(token)
            user_role = payload.get("role")
            
            if user_role is None:
                raise AuthorizationError("Invalid token: missing role")
            
            # Define role hierarchy
            role_hierarchy = {
                "VIEWER": 0,
                "OPERATOR": 1,
                "TENANT_ADMIN": 2,
                "SUPER_ADMIN": 3
            }
            
            user_level = role_hierarchy.get(user_role, -1)
            required_level = role_hierarchy.get(required_role, 999)
            
            if user_level < required_level:
                raise AuthorizationError(f"Insufficient permissions. Required: {required_role}, Current: {user_role}")
            
            return user_role
        
        except (AuthenticationError, AuthorizationError) as e:
            logger.warning(f"Authorization failed: {e.message}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
    
    return role_checker


# Pre-defined role checkers
require_super_admin = require_role("SUPER_ADMIN")
require_tenant_admin = require_role("TENANT_ADMIN")
require_operator = require_role("OPERATOR")
require_viewer = require_role("VIEWER")
