"""
Custom exceptions for the application
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class BaseException(Exception):
    """Base exception class"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class CustomException(BaseException):
    """Custom exception for general use"""
    pass


class ValidationError(BaseException):
    """Validation error"""
    pass


class DatabaseError(BaseException):
    """Database operation error"""
    pass


class ExternalServiceError(BaseException):
    """External service error"""
    pass


class AuthenticationError(BaseException):
    """Authentication error"""
    pass


class AuthorizationError(BaseException):
    """Authorization error"""
    pass


class NotFoundError(BaseException):
    """Resource not found error"""
    pass


class ConflictError(BaseException):
    """Resource conflict error"""
    pass


class RateLimitError(BaseException):
    """Rate limit exceeded error"""
    pass


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "details": exc.details,
        },
    )


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """Handle database errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "message": "A database error occurred",
            "details": exc.details,
        },
    )


async def external_service_error_handler(request: Request, exc: ExternalServiceError) -> JSONResponse:
    """Handle external service errors"""
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "error": "External Service Error",
            "message": exc.message,
            "details": exc.details,
        },
    )


async def authentication_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handle authentication errors"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "Authentication Error",
            "message": exc.message,
            "details": exc.details,
        },
    )


async def authorization_error_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
    """Handle authorization errors"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "Authorization Error",
            "message": exc.message,
            "details": exc.details,
        },
    )


async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handle not found errors"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": exc.message,
            "details": exc.details,
        },
    )


async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
    """Handle conflict errors"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Conflict",
            "message": exc.message,
            "details": exc.details,
        },
    )


async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> JSONResponse:
    """Handle rate limit errors"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate Limit Exceeded",
            "message": exc.message,
            "details": exc.details,
        },
    )
