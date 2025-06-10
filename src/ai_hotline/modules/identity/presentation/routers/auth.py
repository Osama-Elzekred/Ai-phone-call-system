"""Authentication API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.ai_hotline.shared.database import get_db
from src.ai_hotline.shared.exceptions import (
    AuthenticationError,
    EntityNotFoundError,
    BusinessRuleViolationError
)
from src.ai_hotline.modules.identity.application.services.auth_service import AuthenticationService
from src.ai_hotline.modules.identity.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from src.ai_hotline.modules.identity.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository
from src.ai_hotline.modules.identity.presentation.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ChangePasswordRequest,
    UserResponse,
    ErrorResponse,
    RegisterUserRequest,
    RegisterTenantWithAdminRequest
)

# Security scheme
security = HTTPBearer()

# Router
router = APIRouter(tags=["Authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    """Dependency to get authentication service."""
    user_repository = SqlAlchemyUserRepository(db)
    tenant_repository = SqlAlchemyTenantRepository(db)
    return AuthenticationService(user_repository, tenant_repository)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Dependency to get current authenticated user."""
    try:
        token = credentials.credentials
        user = auth_service.verify_token_and_get_user(token)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register-tenant-admin", response_model=LoginResponse)
async def register_tenant_admin(
    request: RegisterTenantWithAdminRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Register a new tenant admin user.
    
    Args:
        request: Tenant registration data
        auth_service: Authentication service
        
    Returns:
        Registered tenant admin user information
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        tenant, user, access_token, refresh_token = await auth_service.register_tenant_with_admin(
            tenant_name=request.tenant_name,
            tenant_display_name=request.tenant_display_name,
            admin_email=request.admin_email,
            admin_password=request.admin_password,
            admin_username=request.admin_username,
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=UserResponse.from_orm(user)
        )
        
    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/register-tenant-user", response_model=LoginResponse)
async def register_tenant_user(
    request: RegisterUserRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    Args:
        request: User registration data
        auth_service: Authentication service
        
    Returns:
        Registered user information
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        user, access_token, refresh_token = await auth_service.register_tenant_user(
            email=request.email,
            password=request.password,
            username=request.username,
            tenant_id=request.tenant_id
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=UserResponse.from_orm(user)
        )
        
    except BusinessRuleViolationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Authenticate user and return access tokens.
    
    Args:
        request: Login credentials
        auth_service: Authentication service
        
    Returns:
        Login response with tokens and user info
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        user, access_token, refresh_token = await auth_service.authenticate_user(
            email=request.email,
            password=request.password
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=UserResponse.from_orm(user)
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        auth_service: Authentication service
        
    Returns:
        New access token
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        access_token = await auth_service.refresh_access_token(
            refresh_token=request.refresh_token
        )
        
        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=30 * 60  # 30 minutes
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.from_orm(current_user)


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Change user password.
    
    Args:
        request: Password change request
        current_user: Current authenticated user
        auth_service: Authentication service
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If password change fails
    """
    try:
        await auth_service.change_password(
            user_id=current_user.id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        
        return {"message": "Password changed successfully"}
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user)
):
    """
    Logout user (client should discard tokens).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # In a more sophisticated implementation, we might:
    # - Add tokens to a blacklist in Redis
    # - Track user sessions
    # For now, we just return success (client handles token disposal)    return {"message": "Logged out successfully"}


# Note: Exception handlers should be registered in main.py with the FastAPI app instance
# These functions can be imported and used for app-level exception handling
