"""Custom exceptions for the application."""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """Base exception for all application exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


# Authentication and Authorization Exceptions
class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(BaseAppException):
    """Raised when authorization fails."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired."""
    pass


class InvalidTokenError(AuthenticationError):
    """Raised when a token is invalid."""
    pass


# Domain Exceptions
class DomainException(BaseAppException):
    """Base exception for domain-related errors."""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""
    pass


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    pass


class ConcurrencyError(DomainException):
    """Raised when concurrent access causes conflicts."""
    pass


class EntityAlreadyExistsError(DomainException):
    """Raised when trying to create an entity that already exists."""
    pass


class InvalidOperationError(DomainException):
    """Raised when an operation is not valid in the current context."""
    pass


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    pass


# Infrastructure Exceptions
class InfrastructureException(BaseAppException):
    """Base exception for infrastructure-related errors."""
    pass


class DatabaseError(InfrastructureException):
    """Raised when database operations fail."""
    pass


class ExternalServiceError(InfrastructureException):
    """Raised when external service calls fail."""
    pass


class FileStorageError(InfrastructureException):
    """Raised when file storage operations fail."""
    pass


class CacheError(InfrastructureException):
    """Raised when cache operations fail."""
    pass


# External API Exceptions
class APIException(InfrastructureException):
    """Base exception for external API errors."""
    pass


class STTServiceError(APIException):
    """Raised when STT service calls fail."""
    pass


class TTSServiceError(APIException):
    """Raised when TTS service calls fail."""
    pass


class LLMServiceError(APIException):
    """Raised when LLM service calls fail."""
    pass


# Validation Exceptions
class ValidationError(BaseAppException):
    """Raised when validation fails."""
    pass


class SchemaValidationError(ValidationError):
    """Raised when schema validation fails."""
    pass


class FileValidationError(ValidationError):
    """Raised when file validation fails."""
    pass


# Tenant Exceptions
class TenantException(BaseAppException):
    """Base exception for tenant-related errors."""
    pass


class TenantNotFoundError(TenantException):
    """Raised when a tenant is not found."""
    pass


class TenantAccessDeniedError(TenantException):
    """Raised when access to a tenant resource is denied."""
    pass


# Call Processing Exceptions
class CallProcessingException(DomainException):
    """Base exception for call processing errors."""
    pass


class AudioProcessingError(CallProcessingException):
    """Raised when audio processing fails."""
    pass


class TranscriptionError(CallProcessingException):
    """Raised when transcription fails."""
    pass


class ResponseGenerationError(CallProcessingException):
    """Raised when response generation fails."""
    pass


# Knowledge Management Exceptions
class KnowledgeException(DomainException):
    """Base exception for knowledge management errors."""
    pass


class DocumentProcessingError(KnowledgeException):
    """Raised when document processing fails."""
    pass


class EmbeddingError(KnowledgeException):
    """Raised when embedding generation fails."""
    pass


class SearchError(KnowledgeException):
    """Raised when knowledge search fails."""
    pass


# Automation Exceptions
class AutomationException(DomainException):
    """Base exception for automation errors."""
    pass


class ActionExecutionError(AutomationException):
    """Raised when automation action execution fails."""
    pass


class WorkflowError(AutomationException):
    """Raised when workflow execution fails."""
    pass
