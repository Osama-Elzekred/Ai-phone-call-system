"""Custom exceptions for the application."""

from .exceptions import (
    # Base exceptions
    BaseAppException,
    
    # Authentication and Authorization
    AuthenticationError,
    AuthorizationError,
    TokenExpiredError,
    InvalidTokenError,
      # Domain exceptions
    DomainException,
    EntityNotFoundError,
    BusinessRuleViolationError,
    ConcurrencyError,
    EntityAlreadyExistsError,
    InvalidOperationError,
    
    # Infrastructure exceptions
    InfrastructureException,
    DatabaseError,
    ExternalServiceError,
    FileStorageError,
    CacheError,
    
    # External API exceptions
    APIException,
    STTServiceError,
    TTSServiceError,
    LLMServiceError,
    
    # Validation exceptions
    ValidationError,
    SchemaValidationError,
    FileValidationError,
    
    # Tenant exceptions
    TenantException,
    TenantNotFoundError,
    TenantAccessDeniedError,
    
    # Call processing exceptions
    CallProcessingException,
    AudioProcessingError,
    TranscriptionError,
    ResponseGenerationError,
    
    # Knowledge management exceptions
    KnowledgeException,
    DocumentProcessingError,
    EmbeddingError,
    SearchError,
    
    # Automation exceptions
    AutomationException,
    ActionExecutionError,
    WorkflowError,
)

__all__ = [
    # Base exceptions
    "BaseAppException",
    
    # Authentication and Authorization
    "AuthenticationError",
    "AuthorizationError", 
    "TokenExpiredError",
    "InvalidTokenError",
      # Domain exceptions
    "DomainException",
    "EntityNotFoundError",
    "BusinessRuleViolationError",
    "ConcurrencyError",
    "EntityAlreadyExistsError",
    "InvalidOperationError",
    
    # Infrastructure exceptions
    "InfrastructureException",
    "DatabaseError",
    "ExternalServiceError",
    "FileStorageError",
    "CacheError",
    
    # External API exceptions
    "APIException",
    "STTServiceError",
    "TTSServiceError",
    "LLMServiceError",
    
    # Validation exceptions
    "ValidationError",
    "SchemaValidationError",
    "FileValidationError",
    
    # Tenant exceptions
    "TenantException",
    "TenantNotFoundError",
    "TenantAccessDeniedError",
    
    # Call processing exceptions
    "CallProcessingException",
    "AudioProcessingError",
    "TranscriptionError",
    "ResponseGenerationError",
    
    # Knowledge management exceptions
    "KnowledgeException",
    "DocumentProcessingError",
    "EmbeddingError",
    "SearchError",
    
    # Automation exceptions
    "AutomationException",
    "ActionExecutionError",
    "WorkflowError",
]
