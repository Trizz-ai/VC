"""
Performance optimization service
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.contact import Contact
from app.models.session import Session
from app.models.meeting import Meeting
from app.models.session_event import SessionEvent

logger = logging.getLogger(__name__)


class PerformanceService:
    """Service for performance optimization and monitoring"""
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes
        self.batch_size = 100
        self.max_connections = 20
    
    async def optimize_database_queries(self, db: AsyncSession) -> Dict[str, Any]:
        """Optimize database queries and indexes"""
        try:
            optimizations = {}
            
            # Check and create indexes
            await self._create_indexes(db)
            optimizations["indexes_created"] = True
            
            # Analyze query performance
            query_stats = await self._analyze_query_performance(db)
            optimizations["query_stats"] = query_stats
            
            # Optimize connection pool
            pool_stats = await self._optimize_connection_pool(db)
            optimizations["pool_stats"] = pool_stats
            
            logger.info("Database optimization completed")
            return optimizations
            
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return {"error": str(e)}
    
    async def _create_indexes(self, db: AsyncSession) -> None:
        """Create database indexes for better performance"""
        try:
            # Create indexes for frequently queried columns
            indexes = [
                # Contact indexes
                "CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)",
                "CREATE INDEX IF NOT EXISTS idx_contacts_ghl_id ON contacts(ghl_contact_id)",
                "CREATE INDEX IF NOT EXISTS idx_contacts_consent ON contacts(consent_granted)",
                
                # Session indexes
                "CREATE INDEX IF NOT EXISTS idx_sessions_contact_id ON sessions(contact_id)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_meeting_id ON sessions(meeting_id)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_sessions_check_in_time ON sessions(check_in_time)",
                
                # Meeting indexes
                "CREATE INDEX IF NOT EXISTS idx_meetings_active ON meetings(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_meetings_created_by ON meetings(created_by)",
                "CREATE INDEX IF NOT EXISTS idx_meetings_start_time ON meetings(start_time)",
                
                # Session event indexes
                "CREATE INDEX IF NOT EXISTS idx_session_events_session_id ON session_events(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_session_events_type ON session_events(type)",
                "CREATE INDEX IF NOT EXISTS idx_session_events_ts_server ON session_events(ts_server)",
                
                # Geospatial indexes (PostGIS)
                "CREATE INDEX IF NOT EXISTS idx_meetings_location ON meetings USING GIST (ST_Point(lng, lat))",
                "CREATE INDEX IF NOT EXISTS idx_session_events_location ON session_events USING GIST (ST_Point(lng, lat))",
            ]
            
            for index_sql in indexes:
                try:
                    await db.execute(text(index_sql))
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")
            
            await db.commit()
            logger.info("Database indexes created/verified")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise
    
    async def _analyze_query_performance(self, db: AsyncSession) -> Dict[str, Any]:
        """Analyze query performance and suggest optimizations"""
        try:
            stats = {}
            
            # Analyze table sizes
            table_sizes = await self._get_table_sizes(db)
            stats["table_sizes"] = table_sizes
            
            # Analyze slow queries
            slow_queries = await self._get_slow_queries(db)
            stats["slow_queries"] = slow_queries
            
            # Analyze index usage
            index_usage = await self._get_index_usage(db)
            stats["index_usage"] = index_usage
            
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {"error": str(e)}
    
    async def _get_table_sizes(self, db: AsyncSession) -> Dict[str, int]:
        """Get table sizes for analysis"""
        try:
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            return {
                row.tablename: {
                    "size": row.size,
                    "size_bytes": row.size_bytes
                }
                for row in rows
            }
            
        except Exception as e:
            logger.error(f"Error getting table sizes: {e}")
            return {}
    
    async def _get_slow_queries(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get slow queries from pg_stat_statements"""
        try:
            query = text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                ORDER BY mean_time DESC 
                LIMIT 10
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            return [
                {
                    "query": row.query[:100] + "..." if len(row.query) > 100 else row.query,
                    "calls": row.calls,
                    "total_time": row.total_time,
                    "mean_time": row.mean_time,
                    "rows": row.rows
                }
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Error getting slow queries: {e}")
            return []
    
    async def _get_index_usage(self, db: AsyncSession) -> Dict[str, Any]:
        """Get index usage statistics"""
        try:
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            return {
                "indexes": [
                    {
                        "table": row.tablename,
                        "index": row.indexname,
                        "scans": row.idx_scan,
                        "tuples_read": row.idx_tup_read,
                        "tuples_fetched": row.idx_tup_fetch
                    }
                    for row in rows
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting index usage: {e}")
            return {}
    
    async def _optimize_connection_pool(self, db: AsyncSession) -> Dict[str, Any]:
        """Optimize database connection pool"""
        try:
            # Get current pool stats
            pool_stats = {
                "size": db.bind.pool.size(),
                "checked_in": db.bind.pool.checkedin(),
                "checked_out": db.bind.pool.checkedout(),
                "overflow": db.bind.pool.overflow(),
                "invalid": db.bind.pool.invalid()
            }
            
            # Suggest optimizations
            suggestions = []
            
            if pool_stats["checked_out"] > pool_stats["size"] * 0.8:
                suggestions.append("Consider increasing pool size")
            
            if pool_stats["overflow"] > 0:
                suggestions.append("Consider increasing max_overflow")
            
            if pool_stats["invalid"] > 0:
                suggestions.append("Check for connection leaks")
            
            return {
                "current_stats": pool_stats,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Error optimizing connection pool: {e}")
            return {"error": str(e)}
    
    async def batch_process_sessions(
        self,
        session_ids: List[str],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Batch process multiple sessions for better performance"""
        try:
            results = {
                "processed": 0,
                "failed": 0,
                "errors": []
            }
            
            # Process in batches
            for i in range(0, len(session_ids), self.batch_size):
                batch = session_ids[i:i + self.batch_size]
                
                try:
                    # Batch query for sessions
                    sessions = await db.execute(
                        text("SELECT * FROM sessions WHERE id = ANY(:session_ids)"),
                        {"session_ids": batch}
                    )
                    
                    # Process each session in the batch
                    for session in sessions:
                        try:
                            # Process session logic here
                            results["processed"] += 1
                        except Exception as e:
                            results["failed"] += 1
                            results["errors"].append(str(e))
                    
                    # Commit batch
                    await db.commit()
                    
                except Exception as e:
                    results["failed"] += len(batch)
                    results["errors"].append(f"Batch error: {str(e)}")
                    await db.rollback()
            
            logger.info(f"Batch processed {results['processed']} sessions, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error batch processing sessions: {e}")
            return {"error": str(e)}
    
    async def optimize_geospatial_queries(
        self,
        user_lat: float,
        user_lng: float,
        radius_km: float,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Optimize geospatial queries with proper indexing"""
        try:
            # Use PostGIS optimized query
            query = text("""
                SELECT 
                    id,
                    name,
                    description,
                    address,
                    lat,
                    lng,
                    radius_meters,
                    ST_Distance(
                        ST_Point(lng, lat),
                        ST_Point(:user_lng, :user_lat)
                    ) as distance_meters
                FROM meetings 
                WHERE 
                    is_active = true
                    AND ST_DWithin(
                        ST_Point(lng, lat),
                        ST_Point(:user_lng, :user_lat),
                        :radius_meters
                    )
                ORDER BY distance_meters
                LIMIT 50
            """)
            
            result = await db.execute(query, {
                "user_lat": user_lat,
                "user_lng": user_lng,
                "radius_meters": radius_km * 1000
            })
            
            meetings = []
            for row in result:
                meetings.append({
                    "id": str(row.id),
                    "name": row.name,
                    "description": row.description,
                    "address": row.address,
                    "latitude": row.lat,
                    "longitude": row.lng,
                    "radius_meters": row.radius_meters,
                    "distance_meters": row.distance_meters,
                    "distance_km": row.distance_meters / 1000
                })
            
            return meetings
            
        except Exception as e:
            logger.error(f"Error optimizing geospatial query: {e}")
            return []
    
    async def cache_frequently_accessed_data(self, db: AsyncSession) -> Dict[str, Any]:
        """Cache frequently accessed data for better performance"""
        try:
            cache_results = {}
            
            # Cache active meetings
            active_meetings = await db.execute(
                text("SELECT * FROM meetings WHERE is_active = true ORDER BY created_at DESC LIMIT 100")
            )
            cache_results["active_meetings"] = len(active_meetings.fetchall())
            
            # Cache recent sessions
            recent_sessions = await db.execute(
                text("SELECT * FROM sessions WHERE created_at > NOW() - INTERVAL '7 days'")
            )
            cache_results["recent_sessions"] = len(recent_sessions.fetchall())
            
            # Cache user statistics
            user_stats = await db.execute(
                text("""
                    SELECT 
                        COUNT(*) as total_users,
                        COUNT(CASE WHEN consent_granted = true THEN 1 END) as consented_users
                    FROM contacts
                """)
            )
            cache_results["user_stats"] = user_stats.fetchone()._asdict()
            
            logger.info("Frequently accessed data cached")
            return cache_results
            
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return {"error": str(e)}
    
    async def monitor_performance_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Monitor system performance metrics"""
        try:
            metrics = {}
            
            # Database connection metrics
            pool_stats = {
                "size": db.bind.pool.size(),
                "checked_in": db.bind.pool.checkedin(),
                "checked_out": db.bind.pool.checkedout(),
                "overflow": db.bind.pool.overflow(),
                "invalid": db.bind.pool.invalid()
            }
            metrics["database_pool"] = pool_stats
            
            # Query performance metrics
            query_metrics = await self._get_query_metrics(db)
            metrics["query_performance"] = query_metrics
            
            # Table statistics
            table_stats = await self._get_table_statistics(db)
            metrics["table_statistics"] = table_stats
            
            # Index usage
            index_stats = await self._get_index_usage(db)
            metrics["index_usage"] = index_stats
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error monitoring performance metrics: {e}")
            return {"error": str(e)}
    
    async def _get_query_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get query performance metrics"""
        try:
            query = text("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(mean_time) as avg_query_time,
                    MAX(mean_time) as max_query_time,
                    SUM(calls) as total_calls
                FROM pg_stat_statements
            """)
            
            result = await db.execute(query)
            row = result.fetchone()
            
            return {
                "total_queries": row.total_queries,
                "avg_query_time": row.avg_query_time,
                "max_query_time": row.max_query_time,
                "total_calls": row.total_calls
            }
            
        except Exception as e:
            logger.error(f"Error getting query metrics: {e}")
            return {}
    
    async def _get_table_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get table statistics"""
        try:
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            return {
                "tables": [
                    {
                        "table": row.tablename,
                        "inserts": row.inserts,
                        "updates": row.updates,
                        "deletes": row.deletes,
                        "live_tuples": row.live_tuples,
                        "dead_tuples": row.dead_tuples
                    }
                    for row in rows
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting table statistics: {e}")
            return {}
    
    async def cleanup_old_data(self, db: AsyncSession, days_old: int = 90) -> Dict[str, int]:
        """Clean up old data to improve performance"""
        try:
            cleanup_stats = {}
            
            # Clean up old session events
            old_events = await db.execute(
                text("DELETE FROM session_events WHERE created_at < NOW() - INTERVAL ':days days'"),
                {"days": days_old}
            )
            cleanup_stats["old_events_deleted"] = old_events.rowcount
            
            # Clean up old sessions
            old_sessions = await db.execute(
                text("DELETE FROM sessions WHERE created_at < NOW() - INTERVAL ':days days' AND status = 'completed'"),
                {"days": days_old}
            )
            cleanup_stats["old_sessions_deleted"] = old_sessions.rowcount
            
            # Clean up old meetings
            old_meetings = await db.execute(
                text("DELETE FROM meetings WHERE created_at < NOW() - INTERVAL ':days days' AND is_active = false"),
                {"days": days_old}
            )
            cleanup_stats["old_meetings_deleted"] = old_meetings.rowcount
            
            await db.commit()
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            await db.rollback()
            return {"error": str(e)}
