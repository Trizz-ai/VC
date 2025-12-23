"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, contacts, meetings, sessions, admin, public, offline, ghl_webhooks
# Temporarily disabled until services are fixed
# from app.api.v1.endpoints import biometric, ai, payments

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    contacts.router,
    prefix="/contacts",
    tags=["contacts"]
)

# Note: /contacts/me must come before /contacts/{contact_id} in the contacts router

api_router.include_router(
    meetings.router,
    prefix="/meetings",
    tags=["meetings"]
)

api_router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["sessions"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)

api_router.include_router(
    public.router,
    prefix="/public",
    tags=["public"]
)

api_router.include_router(
    offline.router,
    prefix="/offline",
    tags=["offline"]
)

api_router.include_router(
    ghl_webhooks.router,
    prefix="/ghl",
    tags=["ghl-webhooks"]
)

# New feature endpoints (temporarily disabled - will fix services to work with AsyncSession)
# api_router.include_router(
#     biometric.router,
#     prefix="/biometric",
#     tags=["biometric"]
# )
# 
# api_router.include_router(
#     ai.router,
#     prefix="/ai",
#     tags=["ai"]
# )
# 
# api_router.include_router(
#     payments.router,
#     prefix="/payments",
#     tags=["payments"]
# )
