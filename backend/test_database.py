"""
Test-specific database configuration for SQLite
"""

import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Set test environment variables
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"

# Create test database engine without pooling parameters
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False
)

# Create test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Mock Redis client for testing
class MockRedis:
    def __init__(self):
        self.data = {}
    
    async def get(self, key):
        return self.data.get(key)
    
    async def set(self, key, value):
        self.data[key] = value
        return True
    
    async def delete(self, key):
        if key in self.data:
            del self.data[key]
        return True
    
    async def close(self):
        pass

mock_redis = MockRedis()

# Patch the database module
import app.core.database
app.core.database.engine = test_engine
app.core.database.AsyncSessionLocal = TestSessionLocal
app.core.database.redis_client = mock_redis

# Now we can import the rest of the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
