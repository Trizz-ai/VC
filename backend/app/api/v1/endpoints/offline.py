"""
Offline operations endpoints for queue-based operations
"""

from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_dependency
from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.offline import (
    OfflineOperationResponse,
    OfflineQueueResponse,
    OfflineRetryRequest,
    OfflineProcessResponse,
)
from app.services.offline_service import OfflineService, OfflineOperation

router = APIRouter()


@router.get("/queue", response_model=List[OfflineOperationResponse])
async def get_pending_operations(
    limit: int = 50,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get pending offline operations for current user"""
    offline_service = OfflineService()
    
    operations = await offline_service.get_pending_operations(
        user_id=current_user.id,
        limit=limit
    )
    
    return [
        OfflineOperationResponse(
            id=op.id,
            operation_type=op.operation_type,
            data=op.data,
            priority=op.priority,
            retry_count=op.retry_count,
            max_retries=op.max_retries,
            created_at=op.created_at,
            last_attempt=op.last_attempt,
            status=op.status
        )
        for op in operations
    ]


@router.get("/failed", response_model=List[OfflineOperationResponse])
async def get_failed_operations(
    limit: int = 50,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get failed offline operations for current user"""
    offline_service = OfflineService()
    
    operations = await offline_service.get_failed_operations(
        user_id=current_user.id,
        limit=limit
    )
    
    return [
        OfflineOperationResponse(
            id=op.id,
            operation_type=op.operation_type,
            data=op.data,
            priority=op.priority,
            retry_count=op.retry_count,
            max_retries=op.max_retries,
            created_at=op.created_at,
            last_attempt=op.last_attempt,
            status=op.status
        )
        for op in operations
    ]


@router.post("/process", response_model=OfflineProcessResponse)
async def process_offline_queue(
    max_operations: int = 10,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Process pending offline operations"""
    offline_service = OfflineService()
    
    result = await offline_service.process_user_queue(
        user_id=current_user.id,
        db=db,
        max_operations=max_operations
    )
    
    return OfflineProcessResponse(**result)


@router.post("/retry", response_model=Dict[str, str])
async def retry_failed_operation(
    retry_request: OfflineRetryRequest,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed operation"""
    offline_service = OfflineService()
    
    success = await offline_service.retry_failed_operation(
        operation_id=retry_request.operation_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed operation not found"
        )
    
    return {"message": "Operation queued for retry"}


@router.delete("/queue", response_model=Dict[str, str])
async def clear_offline_queue(
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Clear all offline operations for current user"""
    offline_service = OfflineService()
    
    success = await offline_service.clear_user_queue(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear queue"
        )
    
    return {"message": "Offline queue cleared successfully"}


@router.get("/status", response_model=OfflineQueueResponse)
async def get_queue_status(
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Get offline queue status for current user"""
    offline_service = OfflineService()
    
    # Get pending operations
    pending_operations = await offline_service.get_pending_operations(
        user_id=current_user.id,
        limit=100
    )
    
    # Get failed operations
    failed_operations = await offline_service.get_failed_operations(
        user_id=current_user.id,
        limit=100
    )
    
    # Count by status
    status_counts = {
        "pending": len([op for op in pending_operations if op.status == "pending"]),
        "processing": len([op for op in pending_operations if op.status == "processing"]),
        "failed": len(failed_operations),
        "total": len(pending_operations) + len(failed_operations)
    }
    
    return OfflineQueueResponse(
        user_id=current_user.id,
        status_counts=status_counts,
        pending_count=len(pending_operations),
        failed_count=len(failed_operations),
        oldest_pending=(
            min(pending_operations, key=lambda x: x.created_at).created_at
            if pending_operations else None
        ),
        newest_failed=(
            max(failed_operations, key=lambda x: x.created_at).created_at
            if failed_operations else None
        )
    )
