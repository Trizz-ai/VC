"""
AI API endpoints for AI-powered features.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.contact import Contact
from app.services.ai_service import AIService

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for AI chat."""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class LegalBriefRequest(BaseModel):
    """Request model for legal brief generation."""
    brief_type: str = Field("compliance_summary", description="Type of brief to generate")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range for the brief")


class MeetingRecommendationsRequest(BaseModel):
    """Request model for meeting recommendations."""
    location: Optional[Dict[str, float]] = Field(None, description="User location (lat, lng)")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Chat with AI assistant.
    
    - **message**: User's message to the AI
    - **conversation_id**: Optional conversation ID for context
    - **context**: Optional additional context (session data, etc.)
    
    Returns AI response and conversation details.
    """
    ai_service = AIService(db)
    
    result = await ai_service.chat(
        user_id=str(current_user.id),
        message=request.message,
        conversation_id=request.conversation_id,
        context=request.context
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "AI chat failed")
        )
    
    return result


@router.post("/legal-brief")
async def generate_legal_brief(
    request: LegalBriefRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI-powered legal brief.
    
    - **brief_type**: Type of brief (compliance_summary, attendance_report, etc.)
    - **date_range**: Optional date range for the brief
    
    Returns generated legal brief.
    """
    ai_service = AIService(db)
    
    result = await ai_service.generate_legal_brief(
        user_id=str(current_user.id),
        brief_type=request.brief_type,
        date_range=request.date_range
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Legal brief generation failed")
        )
    
    return result


@router.post("/recommendations")
async def get_meeting_recommendations(
    request: MeetingRecommendationsRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI-powered meeting recommendations.
    
    - **location**: Optional user location (lat, lng)
    - **preferences**: Optional user preferences
    
    Returns personalized meeting recommendations.
    """
    ai_service = AIService(db)
    
    result = await ai_service.get_meeting_recommendations(
        user_id=str(current_user.id),
        location=request.location,
        preferences=request.preferences
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )
    
    return result


@router.get("/compliance-insights")
async def get_compliance_insights(
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI-powered compliance insights and predictions.
    
    Returns compliance score, risk level, and recommendations.
    """
    ai_service = AIService(db)
    
    result = await ai_service.get_compliance_insights(
        user_id=str(current_user.id)
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get compliance insights"
        )
    
    return result

