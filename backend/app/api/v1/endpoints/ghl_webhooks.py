"""
GoHighLevel webhook endpoints
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.services.ghl_service import GHLService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook")
async def handle_ghl_webhook(
    request: Request
):
    """Handle incoming webhooks from GoHighLevel"""
    try:
        # Get webhook data
        webhook_data = await request.json()
        
        # Log webhook for debugging
        logger.info(f"Received GHL webhook: {webhook_data}")
        
        # Process webhook
        ghl_service = GHLService()
        success = await ghl_service.handle_webhook(webhook_data)
        
        if success:
            return JSONResponse(
                content={"status": "success", "message": "Webhook processed"},
                status_code=200
            )
        else:
            return JSONResponse(
                content={"status": "error", "message": "Webhook processing failed"},
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error processing GHL webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing webhook"
        )


@router.get("/webhook/test")
async def test_webhook():
    """Test webhook endpoint"""
    return {"message": "GHL webhook endpoint is working"}


@router.post("/sync/contact")
async def sync_contact_to_ghl(
    contact_id: str,
    request: Request
):
    """Manually sync contact to GHL"""
    try:
        # This would require database access to get the contact
        # For now, return a placeholder response
        return JSONResponse(
            content={"status": "success", "message": "Contact sync initiated"},
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error syncing contact to GHL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error syncing contact"
        )
