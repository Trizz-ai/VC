"""
Verified Compliance Backend Application
Main FastAPI application entry point
"""

import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import create_tables
from app.core.exceptions import (
    DatabaseError,
    ExternalServiceError,
    ValidationError,
    database_error_handler,
    external_service_error_handler,
    validation_error_handler,
)
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Verified Compliance Backend")
    
    # Create database tables
    await create_tables()
    logger.info("Database tables created successfully")
    
    yield
    
    logger.info("Shutting down Verified Compliance Backend")


# Create FastAPI application
app = FastAPI(
    title="Verified Compliance API",
    description="Mobile attendance tracking system with GPS verification",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
    redirect_slashes=False,  # Disable automatic trailing slash redirects
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS.split(",") if settings.ALLOWED_HOSTS != "*" else ["*"],
)

# Add CORS middleware
# In development, allow all origins (Flutter web uses random ports)
if settings.ENVIRONMENT == "development":
    # For development, allow all origins - set credentials to False to allow "*"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=False,  # Must be False when using "*"
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

# Add exception handlers
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI request validation errors"""
    logger.error(f"Request validation error: {exc.errors()}")
    logger.error(f"Request path: {request.url.path}")
    logger.error(f"Request method: {request.method}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )

app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(DatabaseError, database_error_handler)
app.add_exception_handler(ExternalServiceError, external_service_error_handler)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "verified-compliance-backend",
            "version": "1.0.0",
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "Verified Compliance API",
            "version": "1.0.0",
            "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled",
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
