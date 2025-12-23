"""
Real core authentication tests without mocks, simulations, or hardcoded responses
Tests actual authentication operations with real JWT tokens and password hashing
"""

import pytest
import os
from datetime import datetime, timedelta
from uuid import uuid4
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
    authenticate_user,
    get_current_user
)
from app.models.base import Base
from app.models.contact import Contact


class TestAuthReal:
    """Real authentication tests using actual implementations"""
    
    @pytest.fixture
    async def real_database(self):
        """Create real database for testing"""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create session factory
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        yield async_session
        
        # Cleanup
        await engine.dispose()
    
    @pytest.fixture
    def real_secret_key(self):
        """Create real secret key for testing"""
        return "real-test-secret-key-for-authentication-testing-12345"
    
    @pytest.fixture
    async def real_contact(self, real_database):
        """Create real contact in database"""
        async with real_database() as db:
            contact = Contact(
                email="auth-test@example.com",
                first_name="Auth",
                last_name="Test",
                phone="+1234567890",
                password_hash=get_password_hash("testpassword123"),
                consent_granted=True
            )
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
            return contact
    
    def test_create_access_token_real(self, real_secret_key):
        """Test access token creation with real JWT implementation"""
        # Set real secret key
        original_secret = os.environ.get('SECRET_KEY')
        os.environ['SECRET_KEY'] = real_secret_key
        
        try:
            token = create_access_token(
                data={"sub": "test@example.com", "user_id": str(uuid4())},
                expires_delta=timedelta(minutes=30)
            )
            
            assert token is not None
            assert isinstance(token, str)
            
            # Verify token can be decoded with real JWT
            payload = jwt.decode(
                token,
                real_secret_key,
                algorithms=["HS256"]
            )
            assert payload["sub"] == "test@example.com"
            assert "user_id" in payload
            assert "exp" in payload
            
            # Verify expiration time is reasonable
            exp_time = datetime.fromtimestamp(payload["exp"])
            now = datetime.utcnow()
            time_diff = (exp_time - now).total_seconds()
            assert 25 <= time_diff <= 30  # Should be around 30 minutes
            
        finally:
            # Restore original secret key
            if original_secret:
                os.environ['SECRET_KEY'] = original_secret
            elif 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
    
    def test_create_refresh_token_real(self, real_secret_key):
        """Test refresh token creation with real JWT implementation"""
        # Set real secret key
        original_secret = os.environ.get('SECRET_KEY')
        os.environ['SECRET_KEY'] = real_secret_key
        
        try:
            token = create_refresh_token(
                data={"sub": "test@example.com", "user_id": str(uuid4())}
            )
            
            assert token is not None
            assert isinstance(token, str)
            
            # Verify token can be decoded with real JWT
            payload = jwt.decode(
                token,
                real_secret_key,
                algorithms=["HS256"]
            )
            assert payload["sub"] == "test@example.com"
            assert "user_id" in payload
            assert "exp" in payload
            
            # Verify expiration time is reasonable (should be longer than access token)
            exp_time = datetime.fromtimestamp(payload["exp"])
            now = datetime.utcnow()
            time_diff = (exp_time - now).total_seconds()
            assert time_diff > 3600  # Should be more than 1 hour
            
        finally:
            # Restore original secret key
            if original_secret:
                os.environ['SECRET_KEY'] = original_secret
            elif 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
    
    def test_verify_token_valid_real(self, real_secret_key):
        """Test valid token verification with real JWT"""
        # Set real secret key
        original_secret = os.environ.get('SECRET_KEY')
        os.environ['SECRET_KEY'] = real_secret_key
        
        try:
            # Create real token
            token = create_access_token(
                data={"sub": "test@example.com", "user_id": str(uuid4())},
                expires_delta=timedelta(minutes=30)
            )
            
            # Verify token with real implementation
            payload = verify_token(token)
            assert payload is not None
            assert payload["sub"] == "test@example.com"
            assert "user_id" in payload
            assert "exp" in payload
            
        finally:
            # Restore original secret key
            if original_secret:
                os.environ['SECRET_KEY'] = original_secret
            elif 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
    
    def test_verify_token_invalid_real(self, real_secret_key):
        """Test invalid token verification with real JWT"""
        # Set real secret key
        original_secret = os.environ.get('SECRET_KEY')
        os.environ['SECRET_key'] = real_secret_key
        
        try:
            # Test with invalid token
            with pytest.raises(Exception):
                verify_token("invalid-token")
            
            # Test with expired token
            expired_token = jwt.encode(
                {
                    "sub": "test@example.com",
                    "exp": datetime.utcnow().timestamp() - 3600  # Expired 1 hour ago
                },
                real_secret_key,
                algorithm="HS256"
            )
            
            with pytest.raises(Exception):
                verify_token(expired_token)
            
            # Test with wrong secret key
            wrong_token = jwt.encode(
                {
                    "sub": "test@example.com",
                    "exp": datetime.utcnow().timestamp() + 3600
                },
                "wrong-secret-key",
                algorithm="HS256"
            )
            
            with pytest.raises(Exception):
                verify_token(wrong_token)
                
        finally:
            # Restore original secret key
            if original_secret:
                os.environ['SECRET_KEY'] = original_secret
            elif 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
    
    def test_get_password_hash_real(self):
        """Test password hashing with real implementation"""
        password = "real-test-password-123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 50  # Should be a long hash
        assert hashed.startswith("$2b$")  # Should be bcrypt hash
    
    def test_verify_password_real(self):
        """Test password verification with real implementation"""
        password = "real-test-password-123"
        hashed = get_password_hash(password)
        
        # Test correct password
        assert verify_password(password, hashed) == True
        
        # Test incorrect password
        assert verify_password("wrong-password", hashed) == False
        assert verify_password("", hashed) == False
        assert verify_password(password, "invalid-hash") == False
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success_real(self, real_database, real_contact):
        """Test successful user authentication with real database"""
        async with real_database() as db:
            # Test authentication with real user
            user = await authenticate_user(
                email="auth-test@example.com",
                password="testpassword123",
                db=db
            )
            
            assert user is not None
            assert user.email == "auth-test@example.com"
            assert user.first_name == "Auth"
            assert user.last_name == "Test"
            assert user.consent_granted == True
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password_real(self, real_database, real_contact):
        """Test authentication with wrong password"""
        async with real_database() as db:
            # Test with wrong password
            user = await authenticate_user(
                email="auth-test@example.com",
                password="wrongpassword",
                db=db
            )
            
            assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found_real(self, real_database):
        """Test authentication with non-existent user"""
        async with real_database() as db:
            # Test with non-existent user
            user = await authenticate_user(
                email="nonexistent@example.com",
                password="password",
                db=db
            )
            
            assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_empty_credentials_real(self, real_database):
        """Test authentication with empty credentials"""
        async with real_database() as db:
            # Test with empty email
            user = await authenticate_user(
                email="",
                password="password",
                db=db
            )
            
            assert user is None
            
            # Test with empty password
            user = await authenticate_user(
                email="test@example.com",
                password="",
                db=db
            )
            
            assert user is None
    
    @pytest.mark.asyncio
    async def test_get_current_user_success_real(self, real_database, real_contact):
        """Test getting current user with real database"""
        async with real_database() as db:
            # Test getting real user
            user = await get_current_user(
                email="auth-test@example.com",
                db=db
            )
            
            assert user is not None
            assert user.email == "auth-test@example.com"
            assert user.first_name == "Auth"
            assert user.last_name == "Test"
            assert user.consent_granted == True
    
    @pytest.mark.asyncio
    async def test_get_current_user_not_found_real(self, real_database):
        """Test getting non-existent user"""
        async with real_database() as db:
            # Test with non-existent user
            user = await get_current_user(
                email="nonexistent@example.com",
                db=db
            )
            
            assert user is None
    
    def test_token_expiration_real(self, real_secret_key):
        """Test token expiration with real JWT"""
        # Set real secret key
        original_secret = os.environ.get('SECRET_KEY')
        os.environ['SECRET_KEY'] = real_secret_key
        
        try:
            # Create token with short expiration
            token = create_access_token(
                data={"sub": "test@example.com"},
                expires_delta=timedelta(seconds=1)  # 1 second expiration
            )
            
            # Verify token is valid initially
            payload = verify_token(token)
            assert payload is not None
            assert payload["sub"] == "test@example.com"
            
            # Wait for token to expire
            import time
            time.sleep(2)
            
            # Verify token is now expired
            with pytest.raises(Exception):
                verify_token(token)
                
        finally:
            # Restore original secret key
            if original_secret:
                os.environ['SECRET_KEY'] = original_secret
            elif 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']
    
    def test_password_hash_consistency_real(self):
        """Test password hash consistency with real implementation"""
        password = "consistency-test-password"
        
        # Hash the same password multiple times
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) == True
        assert verify_password(password, hash2) == True
    
    def test_password_hash_security_real(self):
        """Test password hash security with real implementation"""
        password = "security-test-password"
        hashed = get_password_hash(password)
        
        # Hash should not contain the original password
        assert password not in hashed
        
        # Hash should be long enough to be secure
        assert len(hashed) >= 50
        
        # Hash should use bcrypt (starts with $2b$)
        assert hashed.startswith("$2b$")
        
        # Hash should have proper format
        parts = hashed.split('$')
        assert len(parts) == 4
        assert parts[1] == "2b"  # bcrypt version
        assert len(parts[2]) == 2  # cost parameter
        assert len(parts[3]) >= 22  # salt + hash
    
    @pytest.mark.asyncio
    async def test_real_database_operations(self, real_database):
        """Test real database operations and data persistence"""
        async with real_database() as db:
            # Test basic database query
            result = await db.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1
            
            # Test table existence
            result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            table_names = [row[0] for row in tables]
            assert "contacts" in table_names
    
    @pytest.mark.asyncio
    async def test_real_user_authentication_persistence(self, real_database):
        """Test real user authentication and data persistence"""
        async with real_database() as db:
            # Create real user
            contact = Contact(
                email="persistence-test@example.com",
                first_name="Persistence",
                last_name="Test",
                phone="+1234567890",
                password_hash=get_password_hash("persistencepassword123"),
                consent_granted=True
            )
            db.add(contact)
            await db.commit()
            await db.refresh(contact)
            
            # Test authentication
            user = await authenticate_user(
                email="persistence-test@example.com",
                password="persistencepassword123",
                db=db
            )
            
            assert user is not None
            assert user.email == "persistence-test@example.com"
            assert user.first_name == "Persistence"
            assert user.last_name == "Test"
            
            # Verify user was actually persisted in database
            result = await db.execute(
                text("SELECT * FROM contacts WHERE email = :email"),
                {"email": "persistence-test@example.com"}
            )
            db_user = result.fetchone()
            assert db_user is not None
            assert db_user[1] == "persistence-test@example.com"  # email column
            assert db_user[2] == "Persistence"  # first_name column
            assert db_user[3] == "Test"  # last_name column
            assert db_user[6] == True  # consent_granted column