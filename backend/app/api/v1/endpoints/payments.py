"""
Payment API endpoints for subscriptions and payments.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.contact import Contact
from app.services.payment_service import PaymentService

router = APIRouter()


class SubscriptionRequest(BaseModel):
    """Request model for creating a subscription."""
    plan_id: str = Field(..., description="Subscription plan ID")
    payment_method_id: str = Field(..., description="Payment method ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class PaymentRequest(BaseModel):
    """Request model for processing a payment."""
    amount: Decimal = Field(..., description="Payment amount")
    payment_method_id: str = Field(..., description="Payment method ID")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class CancelSubscriptionRequest(BaseModel):
    """Request model for canceling a subscription."""
    reason: Optional[str] = Field(None, description="Cancellation reason")


class InvoiceRequest(BaseModel):
    """Request model for generating an invoice."""
    payment_id: Optional[str] = Field(None, description="Specific payment ID")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range for invoice")


@router.get("/plans")
async def get_subscription_plans(
    db: AsyncSession = Depends(get_db),
):
    """
    Get available subscription plans.
    
    Returns list of available plans with pricing and features.
    """
    payment_service = PaymentService(db)
    
    result = await payment_service.get_subscription_plans()
    
    return result


@router.post("/subscriptions", status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: SubscriptionRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new subscription.
    
    - **plan_id**: Subscription plan identifier
    - **payment_method_id**: Payment method identifier
    - **metadata**: Optional metadata
    
    Returns subscription details and status.
    """
    payment_service = PaymentService(db)
    
    result = await payment_service.create_subscription(
        user_id=str(current_user.id),
        plan_id=request.plan_id,
        payment_method_id=request.payment_method_id,
        metadata=request.metadata
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to create subscription")
        )
    
    return result


@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    request: CancelSubscriptionRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a subscription.
    
    - **subscription_id**: The subscription to cancel
    - **reason**: Optional cancellation reason
    
    Returns cancellation status.
    """
    payment_service = PaymentService(db)
    
    result = await payment_service.cancel_subscription(
        subscription_id=subscription_id,
        reason=request.reason
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Failed to cancel subscription")
        )
    
    return result


@router.post("/payments", status_code=status.HTTP_201_CREATED)
async def process_payment(
    request: PaymentRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a one-time payment.
    
    - **amount**: Payment amount
    - **payment_method_id**: Payment method identifier
    - **description**: Optional payment description
    - **metadata**: Optional metadata
    
    Returns payment details and status.
    """
    payment_service = PaymentService(db)
    
    result = await payment_service.process_payment(
        user_id=str(current_user.id),
        amount=request.amount,
        payment_method_id=request.payment_method_id,
        description=request.description,
        metadata=request.metadata
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Payment processing failed")
        )
    
    return result


@router.get("/payments/history")
async def get_payment_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get payment history for current user.
    
    - **limit**: Maximum number of payments to return (1-100)
    - **offset**: Offset for pagination
    
    Returns list of payments.
    """
    payment_service = PaymentService(db)
    
    result = await payment_service.get_payment_history(
        user_id=str(current_user.id),
        limit=limit,
        offset=offset
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment history"
        )
    
    return result


@router.post("/invoices")
async def generate_invoice(
    request: InvoiceRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an invoice.
    
    - **payment_id**: Optional specific payment ID
    - **date_range**: Optional date range for invoice
    
    Returns invoice details and PDF URL.
    """
    payment_service = PaymentService(db)
    
    result = await payment_service.generate_invoice(
        user_id=str(current_user.id),
        payment_id=request.payment_id,
        date_range=request.date_range
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Failed to generate invoice")
        )
    
    return result

