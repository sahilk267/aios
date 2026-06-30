"""AIOS Custom Exceptions."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AIOSBaseException(Exception):
    """Base exception for AIOS."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AIOSBaseException):
    """Resource not found exception."""
    pass


class ValidationException(AIOSBaseException):
    """Validation error exception."""
    pass


class AuthenticationException(AIOSBaseException):
    """Authentication error exception."""
    pass


class AuthorizationException(AIOSBaseException):
    """Authorization error exception."""
    pass


class ProviderException(AIOSBaseException):
    """AI provider error exception."""
    pass


class WorkflowException(AIOSBaseException):
    """Workflow execution error exception."""
    pass


class AgentException(AIOSBaseException):
    """Agent execution error exception."""
    pass


class PluginException(AIOSBaseException):
    """Plugin error exception."""
    pass


def create_http_exception(
    status_code: int,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> HTTPException:
    """Create an HTTP exception with structured error response."""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": message,
            "details": details or {},
        },
    )


def not_found(resource: str, identifier: Any) -> HTTPException:
    """Create a 404 Not Found exception."""
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        message=f"{resource} not found",
        details={"resource": resource, "identifier": str(identifier)},
    )


def validation_error(message: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """Create a 422 Validation Error exception."""
    return create_http_exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=message,
        details=details,
    )


def unauthorized(message: str = "Authentication required") -> HTTPException:
    """Create a 401 Unauthorized exception."""
    return create_http_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=message,
    )


def forbidden(message: str = "Access denied") -> HTTPException:
    """Create a 403 Forbidden exception."""
    return create_http_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        message=message,
    )
