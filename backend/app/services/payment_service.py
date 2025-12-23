"""
Payment Service for subscription and payment processing.

This service handles:
- Subscription creation and management
- Payment processing
- Invoice generation
- Payment history
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from sqlalchemy.orm import Session
from app.core.config import settings


class PaymentService:
    """Service for handling payment operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        payment_method_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new subscription for a user.
        
        Args:
            user_id: The user's unique identifier
            plan_id: The subscription plan identifier
            payment_method_id: Payment method identifier
            metadata: Optional metadata
            
        Returns:
            Dict containing subscription details
        """
        try:
            # In production: Create Stripe subscription
            # stripe.Subscription.create(
            #     customer=customer_id,
            #     items=[{"price": price_id}],
            #     payment_behavior="default_incomplete"
            # )
            
            subscription_id = f"sub_{uuid.uuid4().hex[:24]}"
            
            # Get plan details
            plan = self._get_plan_details(plan_id)
            
            # Calculate billing dates
            start_date = datetime.utcnow()
            next_billing_date = start_date + timedelta(days=30)
            
            subscription_data = {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "amount": plan["amount"],
                "currency": "USD",
                "status": "active",
                "start_date": start_date.isoformat(),
                "next_billing_date": next_billing_date.isoformat(),
                "payment_method_id": payment_method_id,
                "metadata": metadata or {}
            }
            
            # In production: Store in subscriptions table
            
            return {
                "success": True,
                "subscription": subscription_data,
                "message": "Subscription created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create subscription"
            }
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: The subscription identifier
            reason: Optional cancellation reason
            
        Returns:
            Dict containing cancellation status
        """
        try:
            # In production: Cancel Stripe subscription
            # stripe.Subscription.delete(subscription_id)
            
            return {
                "success": True,
                "subscription_id": subscription_id,
                "status": "canceled",
                "canceled_at": datetime.utcnow().isoformat(),
                "message": "Subscription canceled successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to cancel subscription"
            }
    
    async def process_payment(
        self,
        user_id: str,
        amount: Decimal,
        payment_method_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a one-time payment.
        
        Args:
            user_id: The user's unique identifier
            amount: Payment amount
            payment_method_id: Payment method identifier
            description: Optional payment description
            metadata: Optional metadata
            
        Returns:
            Dict containing payment details
        """
        try:
            # In production: Process Stripe payment
            # stripe.PaymentIntent.create(
            #     amount=int(amount * 100),  # Convert to cents
            #     currency="usd",
            #     payment_method=payment_method_id,
            #     confirm=True
            # )
            
            payment_id = f"pi_{uuid.uuid4().hex[:24]}"
            
            payment_data = {
                "payment_id": payment_id,
                "user_id": user_id,
                "amount": float(amount),
                "currency": "USD",
                "status": "succeeded",
                "payment_method_id": payment_method_id,
                "description": description or "Payment",
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # In production: Store in payments table
            
            return {
                "success": True,
                "payment": payment_data,
                "message": "Payment processed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Payment processing failed"
            }
    
    async def get_payment_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get payment history for a user.
        
        Args:
            user_id: The user's unique identifier
            limit: Maximum number of payments to return
            offset: Offset for pagination
            
        Returns:
            Dict containing payment history
        """
        try:
            # In production: Query payments table
            # Mock payment history
            payments = [
                {
                    "payment_id": f"pi_{uuid.uuid4().hex[:24]}",
                    "amount": 350.00,
                    "currency": "USD",
                    "status": "succeeded",
                    "description": "Monthly subscription - November 2024",
                    "created_at": "2024-11-01T10:00:00Z"
                },
                {
                    "payment_id": f"pi_{uuid.uuid4().hex[:24]}",
                    "amount": 350.00,
                    "currency": "USD",
                    "status": "succeeded",
                    "description": "Monthly subscription - October 2024",
                    "created_at": "2024-10-01T10:00:00Z"
                }
            ]
            
            return {
                "success": True,
                "payments": payments,
                "count": len(payments),
                "total": 2
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "payments": []
            }
    
    async def generate_invoice(
        self,
        user_id: str,
        payment_id: Optional[str] = None,
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate an invoice for a payment or date range.
        
        Args:
            user_id: The user's unique identifier
            payment_id: Optional specific payment ID
            date_range: Optional date range for invoice
            
        Returns:
            Dict containing invoice details
        """
        try:
            invoice_id = f"inv_{uuid.uuid4().hex[:16]}"
            
            # Mock invoice data
            invoice_data = {
                "invoice_id": invoice_id,
                "user_id": user_id,
                "invoice_number": f"INV-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}",
                "date": datetime.utcnow().isoformat(),
                "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "items": [
                    {
                        "description": "Verified Compliance Subscription",
                        "quantity": 1,
                        "unit_price": 350.00,
                        "total": 350.00
                    }
                ],
                "subtotal": 350.00,
                "tax": 0.00,
                "total": 350.00,
                "currency": "USD",
                "status": "paid"
            }
            
            return {
                "success": True,
                "invoice": invoice_data,
                "pdf_url": f"/api/v1/invoices/{invoice_id}/pdf"  # Mock URL
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate invoice"
            }
    
    async def get_subscription_plans(self) -> Dict[str, Any]:
        """
        Get available subscription plans.
        
        Returns:
            Dict containing available plans
        """
        plans = [
            {
                "plan_id": "basic",
                "name": "Basic Plan",
                "description": "Essential compliance tracking",
                "amount": 29.99,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "GPS check-in/check-out",
                    "Session tracking",
                    "Basic reports",
                    "Email support"
                ]
            },
            {
                "plan_id": "professional",
                "name": "Professional Plan",
                "description": "Advanced features for professionals",
                "amount": 79.99,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "All Basic features",
                    "Biometric verification",
                    "AI legal assistant",
                    "Client management",
                    "Advanced analytics",
                    "Priority support"
                ]
            },
            {
                "plan_id": "enterprise",
                "name": "Enterprise Plan",
                "description": "Full-featured solution for organizations",
                "amount": 199.99,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "All Professional features",
                    "Unlimited users",
                    "API access",
                    "Custom integrations",
                    "Dedicated account manager",
                    "24/7 support"
                ]
            }
        ]
        
        return {
            "success": True,
            "plans": plans,
            "count": len(plans)
        }
    
    def _get_plan_details(self, plan_id: str) -> Dict[str, Any]:
        """Get plan details by ID."""
        plans = {
            "basic": {
                "name": "Basic Plan",
                "amount": 29.99,
                "interval": "month"
            },
            "professional": {
                "name": "Professional Plan",
                "amount": 79.99,
                "interval": "month"
            },
            "enterprise": {
                "name": "Enterprise Plan",
                "amount": 199.99,
                "interval": "month"
            }
        }
        
        return plans.get(plan_id, plans["basic"])


# Integration Notes for Production:
# 
# 1. Stripe Integration:
#    import stripe
#    stripe.api_key = settings.STRIPE_SECRET_KEY
#    
#    # Create customer
#    customer = stripe.Customer.create(email=user_email)
#    
#    # Create subscription
#    subscription = stripe.Subscription.create(
#        customer=customer.id,
#        items=[{"price": price_id}]
#    )
#    
#    # Process payment
#    payment_intent = stripe.PaymentIntent.create(
#        amount=amount,
#        currency="usd",
#        payment_method=payment_method_id
#    )
#
# 2. Database Schema:
#    CREATE TABLE subscriptions (
#        id UUID PRIMARY KEY,
#        subscription_id VARCHAR(255) UNIQUE,
#        user_id UUID REFERENCES contacts(id),
#        plan_id VARCHAR(100),
#        status VARCHAR(50),
#        amount DECIMAL(10, 2),
#        currency VARCHAR(3),
#        start_date TIMESTAMP,
#        next_billing_date TIMESTAMP,
#        canceled_at TIMESTAMP,
#        metadata JSONB,
#        created_at TIMESTAMP DEFAULT NOW()
#    );
#    
#    CREATE TABLE payments (
#        id UUID PRIMARY KEY,
#        payment_id VARCHAR(255) UNIQUE,
#        user_id UUID REFERENCES contacts(id),
#        subscription_id UUID REFERENCES subscriptions(id),
#        amount DECIMAL(10, 2),
#        currency VARCHAR(3),
#        status VARCHAR(50),
#        payment_method_id VARCHAR(255),
#        description TEXT,
#        metadata JSONB,
#        created_at TIMESTAMP DEFAULT NOW()
#    );



