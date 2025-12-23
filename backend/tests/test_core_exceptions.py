"""
Real core exceptions tests without mocks, simulations, or hardcoded responses
Tests actual exception handling with real error conditions
"""

import pytest
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    CustomException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    RateLimitException,
    ServiceUnavailableException,
    InternalServerException,
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    request_validation_exception_handler
)


class TestCoreExceptionsReal:
    """Real exception tests using actual implementations"""
    
    def test_custom_exception_creation_real(self):
        """Test custom exception creation with real implementation"""
        # Test basic custom exception
        exc = CustomException("Test error message")
        assert str(exc) == "Test error message"
        assert exc.status_code == 500
        assert exc.detail == "Test error message"
        
        # Test custom exception with status code
        exc = CustomException("Test error message", status_code=400)
        assert str(exc) == "Test error message"
        assert exc.status_code == 400
        assert exc.detail == "Test error message"
    
    def test_validation_exception_creation_real(self):
        """Test validation exception creation with real implementation"""
        exc = ValidationException("Validation error message")
        assert str(exc) == "Validation error message"
        assert exc.status_code == 422
        assert exc.detail == "Validation error message"
    
    def test_authentication_exception_creation_real(self):
        """Test authentication exception creation with real implementation"""
        exc = AuthenticationException("Authentication error message")
        assert str(exc) == "Authentication error message"
        assert exc.status_code == 401
        assert exc.detail == "Authentication error message"
    
    def test_authorization_exception_creation_real(self):
        """Test authorization exception creation with real implementation"""
        exc = AuthorizationException("Authorization error message")
        assert str(exc) == "Authorization error message"
        assert exc.status_code == 403
        assert exc.detail == "Authorization error message"
    
    def test_not_found_exception_creation_real(self):
        """Test not found exception creation with real implementation"""
        exc = NotFoundException("Not found error message")
        assert str(exc) == "Not found error message"
        assert exc.status_code == 404
        assert exc.detail == "Not found error message"
    
    def test_conflict_exception_creation_real(self):
        """Test conflict exception creation with real implementation"""
        exc = ConflictException("Conflict error message")
        assert str(exc) == "Conflict error message"
        assert exc.status_code == 409
        assert exc.detail == "Conflict error message"
    
    def test_rate_limit_exception_creation_real(self):
        """Test rate limit exception creation with real implementation"""
        exc = RateLimitException("Rate limit error message")
        assert str(exc) == "Rate limit error message"
        assert exc.status_code == 429
        assert exc.detail == "Rate limit error message"
    
    def test_service_unavailable_exception_creation_real(self):
        """Test service unavailable exception creation with real implementation"""
        exc = ServiceUnavailableException("Service unavailable error message")
        assert str(exc) == "Service unavailable error message"
        assert exc.status_code == 503
        assert exc.detail == "Service unavailable error message"
    
    def test_internal_server_exception_creation_real(self):
        """Test internal server exception creation with real implementation"""
        exc = InternalServerException("Internal server error message")
        assert str(exc) == "Internal server error message"
        assert exc.status_code == 500
        assert exc.detail == "Internal server error message"
    
    def test_custom_exception_handler_real(self):
        """Test custom exception handler with real implementation"""
        # Create real request object
        request = Request({"type": "http", "method": "GET", "url": "http://test.com"})
        
        # Create real custom exception
        exc = CustomException("Test error message", status_code=400)
        
        # Test exception handler
        response = custom_exception_handler(request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        
        # Verify response content
        response_data = response.body.decode()
        assert "Test error message" in response_data
        assert "error" in response_data
        assert "detail" in response_data
    
    def test_http_exception_handler_real(self):
        """Test HTTP exception handler with real implementation"""
        # Create real request object
        request = Request({"type": "http", "method": "GET", "url": "http://test.com"})
        
        # Create real HTTP exception
        exc = HTTPException(status_code=404, detail="Not found")
        
        # Test exception handler
        response = http_exception_handler(request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        
        # Verify response content
        response_data = response.body.decode()
        assert "Not found" in response_data
        assert "error" in response_data
        assert "detail" in response_data
    
    def test_validation_exception_handler_real(self):
        """Test validation exception handler with real implementation"""
        # Create real request object
        request = Request({"type": "http", "method": "GET", "url": "http://test.com"})
        
        # Create real validation exception
        exc = ValidationException("Validation error message")
        
        # Test exception handler
        response = validation_exception_handler(request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422
        
        # Verify response content
        response_data = response.body.decode()
        assert "Validation error message" in response_data
        assert "error" in response_data
        assert "detail" in response_data
    
    def test_request_validation_exception_handler_real(self):
        """Test request validation exception handler with real implementation"""
        # Create real request object
        request = Request({"type": "http", "method": "GET", "url": "http://test.com"})
        
        # Create real validation exception
        exc = ValueError("Request validation error")
        
        # Test exception handler
        response = request_validation_exception_handler(request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422
        
        # Verify response content
        response_data = response.body.decode()
        assert "Request validation error" in response_data
        assert "error" in response_data
        assert "detail" in response_data
    
    def test_exception_inheritance_real(self):
        """Test exception inheritance with real implementation"""
        # Test that custom exceptions inherit from base exception
        exc = CustomException("Test message")
        assert isinstance(exc, Exception)
        assert isinstance(exc, CustomException)
        
        # Test that specific exceptions inherit from custom exception
        exc = ValidationException("Test message")
        assert isinstance(exc, Exception)
        assert isinstance(exc, CustomException)
        assert isinstance(exc, ValidationException)
        
        exc = AuthenticationException("Test message")
        assert isinstance(exc, Exception)
        assert isinstance(exc, CustomException)
        assert isinstance(exc, AuthenticationException)
    
    def test_exception_status_codes_real(self):
        """Test exception status codes with real implementation"""
        # Test all status codes are correct
        assert ValidationException("").status_code == 422
        assert AuthenticationException("").status_code == 401
        assert AuthorizationException("").status_code == 403
        assert NotFoundException("").status_code == 404
        assert ConflictException("").status_code == 409
        assert RateLimitException("").status_code == 429
        assert ServiceUnavailableException("").status_code == 503
        assert InternalServerException("").status_code == 500
        assert CustomException("").status_code == 500
    
    def test_exception_message_handling_real(self):
        """Test exception message handling with real implementation"""
        # Test empty message
        exc = CustomException("")
        assert str(exc) == ""
        assert exc.detail == ""
        
        # Test None message
        exc = CustomException(None)
        assert str(exc) == "None"
        assert exc.detail == "None"
        
        # Test long message
        long_message = "This is a very long error message that should be handled properly by the exception system"
        exc = CustomException(long_message)
        assert str(exc) == long_message
        assert exc.detail == long_message
        
        # Test special characters
        special_message = "Error with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        exc = CustomException(special_message)
        assert str(exc) == special_message
        assert exc.detail == special_message
    
    def test_exception_handler_error_formatting_real(self):
        """Test exception handler error formatting with real implementation"""
        # Create real request object
        request = Request({"type": "http", "method": "GET", "url": "http://test.com"})
        
        # Test different exception types
        exceptions = [
            CustomException("Custom error", status_code=400),
            ValidationException("Validation error"),
            AuthenticationException("Authentication error"),
            AuthorizationException("Authorization error"),
            NotFoundException("Not found error"),
            ConflictException("Conflict error"),
            RateLimitException("Rate limit error"),
            ServiceUnavailableException("Service unavailable error"),
            InternalServerException("Internal server error")
        ]
        
        for exc in exceptions:
            response = custom_exception_handler(request, exc)
            assert isinstance(response, JSONResponse)
            assert response.status_code == exc.status_code
            
            # Verify response content structure
            response_data = response.body.decode()
            assert "error" in response_data
            assert "detail" in response_data
            assert exc.detail in response_data
    
    def test_exception_handler_request_context_real(self):
        """Test exception handler request context with real implementation"""
        # Create real request object with different methods
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        for method in methods:
            request = Request({
                "type": "http",
                "method": method,
                "url": f"http://test.com/{method.lower()}"
            })
            
            exc = CustomException(f"Error for {method} request")
            response = custom_exception_handler(request, exc)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == 500
            
            # Verify response content
            response_data = response.body.decode()
            assert f"Error for {method} request" in response_data
    
    def test_exception_handler_status_code_preservation_real(self):
        """Test exception handler status code preservation with real implementation"""
        # Create real request object
        request = Request({"type": "http", "method": "GET", "url": "http://test.com"})
        
        # Test different status codes
        status_codes = [200, 201, 400, 401, 403, 404, 409, 422, 429, 500, 503]
        
        for status_code in status_codes:
            exc = CustomException(f"Error with status {status_code}", status_code=status_code)
            response = custom_exception_handler(request, exc)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == status_code
            
            # Verify response content
            response_data = response.body.decode()
            assert f"Error with status {status_code}" in response_data