"""
Offline service for queue-based operations when network is unavailable
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_redis
from app.models.session import Session
from app.models.session_event import SessionEvent, EventType
from app.services.location_service import LocationData
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class OfflineOperation:
    """Represents an offline operation to be queued"""
    
    def __init__(
        self,
        operation_type: str,
        data: Dict[str, Any],
        user_id: UUID,
        priority: int = 1,
        max_retries: int = 3
    ):
        self.id = str(uuid4())
        self.operation_type = operation_type
        self.data = data
        self.user_id = user_id
        self.priority = priority
        self.max_retries = max_retries
        self.retry_count = 0
        self.created_at = datetime.utcnow()
        self.last_attempt = None
        self.status = "pending"  # pending, processing, failed, completed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "operation_type": self.operation_type,
            "data": self.data,
            "user_id": str(self.user_id),
            "priority": self.priority,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "last_attempt": self.last_attempt.isoformat() if self.last_attempt else None,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OfflineOperation":
        """Create from dictionary"""
        operation = cls(
            operation_type=data["operation_type"],
            data=data["data"],
            user_id=UUID(data["user_id"]),
            priority=data.get("priority", 1),
            max_retries=data.get("max_retries", 3)
        )
        operation.id = data["id"]
        operation.retry_count = data.get("retry_count", 0)
        operation.created_at = datetime.fromisoformat(data["created_at"])
        operation.last_attempt = (
            datetime.fromisoformat(data["last_attempt"])
            if data.get("last_attempt") else None
        )
        operation.status = data.get("status", "pending")
        return operation


class OfflineService:
    """Service for managing offline operations"""
    
    def __init__(self):
        self.redis_client = None
        self.session_service = SessionService()
        self.queue_key_prefix = "offline_queue"
        self.failed_key_prefix = "offline_failed"
        self.max_queue_size = 1000
        self.retry_delay_minutes = 5
    
    async def _get_redis(self) -> redis.Redis:
        """Get Redis client"""
        if not self.redis_client:
            self.redis_client = await get_redis()
        return self.redis_client
    
    async def queue_operation(
        self,
        operation_type: str,
        data: Dict[str, Any],
        user_id: UUID,
        priority: int = 1
    ) -> str:
        """Queue an operation for offline processing"""
        try:
            redis_client = await self._get_redis()
            
            # Create operation
            operation = OfflineOperation(
                operation_type=operation_type,
                data=data,
                user_id=user_id,
                priority=priority
            )
            
            # Store in Redis queue
            queue_key = f"{self.queue_key_prefix}:{user_id}"
            operation_json = json.dumps(operation.to_dict())
            
            # Use priority score for ordering
            score = operation.priority * 1000000 - int(operation.created_at.timestamp())
            await redis_client.zadd(queue_key, {operation_json: score})
            
            # Set expiration for queue (7 days)
            await redis_client.expire(queue_key, 7 * 24 * 60 * 60)
            
            logger.info(f"Queued operation {operation.id} for user {user_id}")
            return operation.id
            
        except Exception as e:
            logger.error(f"Error queueing operation: {e}")
            raise
    
    async def get_pending_operations(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[OfflineOperation]:
        """Get pending operations for a user"""
        try:
            redis_client = await self._get_redis()
            queue_key = f"{self.queue_key_prefix}:{user_id}"
            
            # Get operations from queue (highest priority first)
            operations_data = await redis_client.zrevrange(
                queue_key, 0, limit - 1, withscores=True
            )
            
            operations = []
            for operation_json, score in operations_data:
                try:
                    operation_dict = json.loads(operation_json)
                    operation = OfflineOperation.from_dict(operation_dict)
                    operations.append(operation)
                except Exception as e:
                    logger.warning(f"Error parsing operation: {e}")
                    continue
            
            return operations
            
        except Exception as e:
            logger.error(f"Error getting pending operations: {e}")
            return []
    
    async def process_operation(
        self,
        operation: OfflineOperation,
        db: AsyncSession
    ) -> bool:
        """Process a single offline operation"""
        try:
            operation.status = "processing"
            operation.last_attempt = datetime.utcnow()
            
            success = False
            
            if operation.operation_type == "check_in":
                success = await self._process_check_in(operation, db)
            elif operation.operation_type == "check_out":
                success = await self._process_check_out(operation, db)
            elif operation.operation_type == "create_session":
                success = await self._process_create_session(operation, db)
            elif operation.operation_type == "end_session":
                success = await self._process_end_session(operation, db)
            else:
                logger.warning(f"Unknown operation type: {operation.operation_type}")
                return False
            
            if success:
                operation.status = "completed"
                await self._remove_operation(operation)
                logger.info(f"Successfully processed operation {operation.id}")
            else:
                operation.retry_count += 1
                if operation.retry_count >= operation.max_retries:
                    operation.status = "failed"
                    await self._move_to_failed(operation)
                    logger.error(f"Operation {operation.id} failed after {operation.max_retries} retries")
                else:
                    operation.status = "pending"
                    await self._update_operation(operation)
                    logger.warning(f"Operation {operation.id} failed, will retry (attempt {operation.retry_count})")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing operation {operation.id}: {e}")
            operation.retry_count += 1
            operation.status = "failed" if operation.retry_count >= operation.max_retries else "pending"
            await self._update_operation(operation)
            return False
    
    async def process_user_queue(
        self,
        user_id: UUID,
        db: AsyncSession,
        max_operations: int = 10
    ) -> Dict[str, int]:
        """Process all pending operations for a user"""
        try:
            operations = await self.get_pending_operations(user_id, max_operations)
            
            processed = 0
            failed = 0
            
            for operation in operations:
                success = await self.process_operation(operation, db)
                if success:
                    processed += 1
                else:
                    failed += 1
            
            return {
                "processed": processed,
                "failed": failed,
                "total": len(operations)
            }
            
        except Exception as e:
            logger.error(f"Error processing user queue for {user_id}: {e}")
            return {"processed": 0, "failed": 0, "total": 0}
    
    async def _process_check_in(
        self,
        operation: OfflineOperation,
        db: AsyncSession
    ) -> bool:
        """Process check-in operation"""
        try:
            data = operation.data
            location_data = LocationData(
                latitude=data["latitude"],
                longitude=data["longitude"],
                accuracy=data.get("accuracy"),
                altitude=data.get("altitude"),
                speed=data.get("speed"),
                heading=data.get("heading"),
                timestamp=data.get("timestamp"),
            )
            
            event = await self.session_service.check_in(
                session_id=UUID(data["session_id"]),
                location_data=location_data,
                notes=data.get("notes"),
                db=db
            )
            
            return event is not None
            
        except Exception as e:
            logger.error(f"Error processing check-in: {e}")
            return False
    
    async def _process_check_out(
        self,
        operation: OfflineOperation,
        db: AsyncSession
    ) -> bool:
        """Process check-out operation"""
        try:
            data = operation.data
            location_data = LocationData(
                latitude=data["latitude"],
                longitude=data["longitude"],
                accuracy=data.get("accuracy"),
                altitude=data.get("altitude"),
                speed=data.get("speed"),
                heading=data.get("heading"),
                timestamp=data.get("timestamp"),
            )
            
            event = await self.session_service.check_out(
                session_id=UUID(data["session_id"]),
                location_data=location_data,
                notes=data.get("notes"),
                db=db
            )
            
            return event is not None
            
        except Exception as e:
            logger.error(f"Error processing check-out: {e}")
            return False
    
    async def _process_create_session(
        self,
        operation: OfflineOperation,
        db: AsyncSession
    ) -> bool:
        """Process create session operation"""
        try:
            data = operation.data
            session = await self.session_service.create_session(
                contact_id=UUID(data["contact_id"]),
                meeting_id=UUID(data["meeting_id"]),
                notes=data.get("notes"),
                db=db
            )
            
            return session is not None
            
        except Exception as e:
            logger.error(f"Error processing create session: {e}")
            return False
    
    async def _process_end_session(
        self,
        operation: OfflineOperation,
        db: AsyncSession
    ) -> bool:
        """Process end session operation"""
        try:
            data = operation.data
            success = await self.session_service.end_session(
                session_id=UUID(data["session_id"]),
                reason=data.get("reason", "Offline end"),
                db=db
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing end session: {e}")
            return False
    
    async def _remove_operation(self, operation: OfflineOperation):
        """Remove operation from queue"""
        try:
            redis_client = await self._get_redis()
            queue_key = f"{self.queue_key_prefix}:{operation.user_id}"
            
            # Remove from queue
            await redis_client.zremrangebyscore(queue_key, "-inf", "+inf")
            
        except Exception as e:
            logger.error(f"Error removing operation: {e}")
    
    async def _move_to_failed(self, operation: OfflineOperation):
        """Move operation to failed queue"""
        try:
            redis_client = await self._get_redis()
            failed_key = f"{self.failed_key_prefix}:{operation.user_id}"
            
            operation_json = json.dumps(operation.to_dict())
            await redis_client.lpush(failed_key, operation_json)
            
            # Set expiration for failed queue (30 days)
            await redis_client.expire(failed_key, 30 * 24 * 60 * 60)
            
        except Exception as e:
            logger.error(f"Error moving operation to failed: {e}")
    
    async def _update_operation(self, operation: OfflineOperation):
        """Update operation in queue"""
        try:
            redis_client = await self._get_redis()
            queue_key = f"{self.queue_key_prefix}:{operation.user_id}"
            
            operation_json = json.dumps(operation.to_dict())
            score = operation.priority * 1000000 - int(operation.created_at.timestamp())
            
            # Update in queue
            await redis_client.zadd(queue_key, {operation_json: score})
            
        except Exception as e:
            logger.error(f"Error updating operation: {e}")
    
    async def get_failed_operations(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[OfflineOperation]:
        """Get failed operations for a user"""
        try:
            redis_client = await self._get_redis()
            failed_key = f"{self.failed_key_prefix}:{user_id}"
            
            operations_data = await redis_client.lrange(failed_key, 0, limit - 1)
            
            operations = []
            for operation_json in operations_data:
                try:
                    operation_dict = json.loads(operation_json)
                    operation = OfflineOperation.from_dict(operation_dict)
                    operations.append(operation)
                except Exception as e:
                    logger.warning(f"Error parsing failed operation: {e}")
                    continue
            
            return operations
            
        except Exception as e:
            logger.error(f"Error getting failed operations: {e}")
            return []
    
    async def retry_failed_operation(
        self,
        operation_id: str,
        user_id: UUID
    ) -> bool:
        """Retry a failed operation"""
        try:
            redis_client = await self._get_redis()
            failed_key = f"{self.failed_key_prefix}:{user_id}"
            queue_key = f"{self.queue_key_prefix}:{user_id}"
            
            # Find and remove from failed queue
            operations_data = await redis_client.lrange(failed_key, 0, -1)
            
            for operation_json in operations_data:
                operation_dict = json.loads(operation_json)
                if operation_dict["id"] == operation_id:
                    # Remove from failed queue
                    await redis_client.lrem(failed_key, 1, operation_json)
                    
                    # Reset retry count and add back to queue
                    operation_dict["retry_count"] = 0
                    operation_dict["status"] = "pending"
                    
                    operation = OfflineOperation.from_dict(operation_dict)
                    operation_json = json.dumps(operation.to_dict())
                    score = operation.priority * 1000000 - int(operation.created_at.timestamp())
                    
                    await redis_client.zadd(queue_key, {operation_json: score})
                    
                    logger.info(f"Retried operation {operation_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error retrying operation: {e}")
            return False
    
    async def clear_user_queue(self, user_id: UUID) -> bool:
        """Clear all operations for a user"""
        try:
            redis_client = await self._get_redis()
            queue_key = f"{self.queue_key_prefix}:{user_id}"
            failed_key = f"{self.failed_key_prefix}:{user_id}"
            
            await redis_client.delete(queue_key)
            await redis_client.delete(failed_key)
            
            logger.info(f"Cleared queue for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing user queue: {e}")
            return False
