"""
Unit tests for core configuration module
"""

import pytest
import os
import tempfile
from pathlib import Path

from app.core.config import Settings


class TestSettings:
    """Test cases for Settings configuration"""
    
    def test_default_settings(self):
        """Test default configuration values"""
        settings = Settings()
        
        # Test default values
        assert settings.ENVIRONMENT == "development"
        assert settings.DEBUG == True
        assert settings.DATABASE_URL is not None
        assert settings.REDIS_URL is not None
        assert settings.SECRET_KEY is not None
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
        assert settings.CORS_ORIGINS == "*"
        assert settings.ALLOWED_HOSTS == "*"
    
    def test_environment_override(self):
        """Test environment variable override using real environment variables"""
        # Set real environment variables
        original_env = os.environ.copy()
        try:
            os.environ['ENVIRONMENT'] = 'production'
            os.environ['DEBUG'] = 'false'
            os.environ['SECRET_KEY'] = 'test-secret-key'
            os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'
            
            settings = Settings()
            assert settings.ENVIRONMENT == "production"
            assert settings.DEBUG == False
            assert settings.SECRET_KEY == "test-secret-key"
            assert settings.DATABASE_URL == "postgresql://test:test@localhost/test"
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_validation_rules(self):
        """Test configuration validation with real environment variables"""
        original_env = os.environ.copy()
        try:
            # Test invalid environment
            os.environ['ENVIRONMENT'] = 'invalid'
            with pytest.raises(ValueError):
                Settings()
            
            # Test invalid debug value
            os.environ['DEBUG'] = 'invalid'
            with pytest.raises(ValueError):
                Settings()
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_database_configuration(self):
        """Test database configuration"""
        settings = Settings()
        
        # Test database URL format
        assert "postgresql" in settings.DATABASE_URL or "sqlite" in settings.DATABASE_URL
        
        # Test Redis URL format
        assert "redis" in settings.REDIS_URL
    
    def test_security_configuration(self):
        """Test security-related configuration"""
        settings = Settings()
        
        # Test secret key is set
        assert len(settings.SECRET_KEY) >= 32
        
        # Test token expiration times
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0
        
        # Test CORS configuration
        assert isinstance(settings.CORS_ORIGINS, str)
        assert isinstance(settings.ALLOWED_HOSTS, str)
    
    def test_external_service_configuration(self):
        """Test external service configuration"""
        settings = Settings()
        
        # Test optional external service keys
        assert hasattr(settings, 'GHL_API_KEY')
        assert hasattr(settings, 'GOOGLE_MAPS_API_KEY')
        assert hasattr(settings, 'SENDGRID_API_KEY')
        assert hasattr(settings, 'FCM_SERVER_KEY')
    
    def test_logging_configuration(self):
        """Test logging configuration"""
        settings = Settings()
        
        # Test logging level
        assert hasattr(settings, 'LOG_LEVEL')
        assert settings.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    def test_development_vs_production(self):
        """Test development vs production settings using real environment variables"""
        original_env = os.environ.copy()
        try:
            # Development settings
            os.environ['ENVIRONMENT'] = 'development'
            dev_settings = Settings()
            assert dev_settings.ENVIRONMENT == "development"
            assert dev_settings.DEBUG == True
            
            # Production settings
            os.environ['ENVIRONMENT'] = 'production'
            prod_settings = Settings()
            assert prod_settings.ENVIRONMENT == "production"
            assert prod_settings.DEBUG == False
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
    
    def test_database_pool_configuration(self):
        """Test database connection pool settings"""
        settings = Settings()
        
        # Test pool settings exist
        assert hasattr(settings, 'DB_POOL_SIZE')
        assert hasattr(settings, 'DB_MAX_OVERFLOW')
        assert hasattr(settings, 'DB_POOL_TIMEOUT')
        
        # Test pool values are positive
        assert settings.DB_POOL_SIZE > 0
        assert settings.DB_MAX_OVERFLOW >= 0
        assert settings.DB_POOL_TIMEOUT > 0
    
    def test_redis_configuration(self):
        """Test Redis configuration"""
        settings = Settings()
        
        # Test Redis settings exist
        assert hasattr(settings, 'REDIS_HOST')
        assert hasattr(settings, 'REDIS_PORT')
        assert hasattr(settings, 'REDIS_DB')
        
        # Test Redis values are valid
        assert isinstance(settings.REDIS_HOST, str)
        assert isinstance(settings.REDIS_PORT, int)
        assert 0 <= settings.REDIS_DB <= 15
    
    def test_api_configuration(self):
        """Test API configuration"""
        settings = Settings()
        
        # Test API settings
        assert hasattr(settings, 'API_V1_STR')
        assert hasattr(settings, 'PROJECT_NAME')
        
        # Test API values
        assert settings.API_V1_STR == "/api/v1"
        assert settings.PROJECT_NAME == "Verified Compliance API"
    
    def test_file_upload_configuration(self):
        """Test file upload configuration"""
        settings = Settings()
        
        # Test upload settings
        assert hasattr(settings, 'MAX_FILE_SIZE')
        assert hasattr(settings, 'ALLOWED_FILE_TYPES')
        
        # Test upload values
        assert settings.MAX_FILE_SIZE > 0
        assert isinstance(settings.ALLOWED_FILE_TYPES, list)
        assert len(settings.ALLOWED_FILE_TYPES) > 0
