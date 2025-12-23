#!/usr/bin/env python3
"""
Test environment setup for Verified Compliance Backend
Sets up real environment variables for testing
"""

import os
import sys
from pathlib import Path

def setup_test_environment():
    """Setup test environment variables"""
    # Set required environment variables for testing
    os.environ['SECRET_KEY'] = 'test-secret-key-for-verified-compliance-backend-testing-12345'
    os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///:memory:'
    os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
    os.environ['ENVIRONMENT'] = 'testing'
    os.environ['DEBUG'] = 'true'
    os.environ['LOG_LEVEL'] = 'INFO'
    
    # Set optional environment variables
    os.environ['GHL_API_KEY'] = 'test-ghl-api-key'
    os.environ['GOOGLE_MAPS_API_KEY'] = 'test-google-maps-api-key'
    os.environ['SENDGRID_API_KEY'] = 'test-sendgrid-api-key'
    os.environ['FCM_SERVER_KEY'] = 'test-fcm-server-key'
    
    # Set CORS and security settings
    os.environ['CORS_ORIGINS'] = '*'
    os.environ['ALLOWED_HOSTS'] = '*'
    
    # Set token expiration settings
    os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'] = '30'
    os.environ['REFRESH_TOKEN_EXPIRE_DAYS'] = '7'
    
    # Set database pool settings
    os.environ['DB_POOL_SIZE'] = '5'
    os.environ['DB_MAX_OVERFLOW'] = '10'
    os.environ['DB_POOL_TIMEOUT'] = '30'
    
    # Set Redis settings
    os.environ['REDIS_HOST'] = 'localhost'
    os.environ['REDIS_PORT'] = '6379'
    os.environ['REDIS_DB'] = '0'
    os.environ['REDIS_MAX_CONNECTIONS'] = '100'
    
    # Set API settings
    os.environ['API_V1_STR'] = '/api/v1'
    os.environ['PROJECT_NAME'] = 'Verified Compliance API'
    
    # Set file upload settings
    os.environ['MAX_FILE_SIZE'] = '10485760'  # 10MB
    os.environ['ALLOWED_FILE_TYPES'] = 'jpg,jpeg,png,pdf,doc,docx'
    
    print("Test environment variables set successfully")

if __name__ == "__main__":
    setup_test_environment()
