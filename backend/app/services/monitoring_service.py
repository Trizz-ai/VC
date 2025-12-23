"""
Monitoring and logging service
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for system monitoring and alerting"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = []
        self.health_checks = {}
        self.performance_thresholds = {
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
            "memory_usage_percent": 80.0,
            "cpu_usage_percent": 80.0,
            "database_connections": 80
        }
    
    async def collect_system_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            metrics = {}
            
            # Database metrics
            db_metrics = await self._collect_database_metrics(db)
            metrics["database"] = db_metrics
            
            # Application metrics
            app_metrics = await self._collect_application_metrics()
            metrics["application"] = app_metrics
            
            # Performance metrics
            perf_metrics = await self._collect_performance_metrics(db)
            metrics["performance"] = perf_metrics
            
            # Health metrics
            health_metrics = await self._collect_health_metrics(db)
            metrics["health"] = health_metrics
            
            # Store metrics
            self.metrics = metrics
            
            logger.info("System metrics collected successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {"error": str(e)}
    
    async def _collect_database_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Collect database-specific metrics"""
        try:
            metrics = {}
            
            # Connection pool stats
            pool_stats = {
                "size": db.bind.pool.size(),
                "checked_in": db.bind.pool.checkedin(),
                "checked_out": db.bind.pool.checkedout(),
                "overflow": db.bind.pool.overflow(),
                "invalid": db.bind.pool.invalid()
            }
            metrics["connection_pool"] = pool_stats
            
            # Database size
            size_query = text("SELECT pg_database_size(current_database()) as db_size")
            result = await db.execute(size_query)
            db_size = result.fetchone()
            metrics["database_size_bytes"] = db_size.db_size
            
            # Table statistics
            table_stats = await self._get_table_statistics(db)
            metrics["tables"] = table_stats
            
            # Query performance
            query_stats = await self._get_query_statistics(db)
            metrics["queries"] = query_stats
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            return {"error": str(e)}
    
    async def _collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        try:
            metrics = {}
            
            # Memory usage
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            metrics["memory"] = {
                "rss": memory_info.rss,
                "vms": memory_info.vms,
                "percent": process.memory_percent()
            }
            
            # CPU usage
            metrics["cpu"] = {
                "percent": process.cpu_percent(),
                "num_threads": process.num_threads()
            }
            
            # Process info
            metrics["process"] = {
                "pid": process.pid,
                "create_time": process.create_time(),
                "status": process.status()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return {"error": str(e)}
    
    async def _collect_performance_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Collect performance metrics"""
        try:
            metrics = {}
            
            # Response time metrics
            metrics["response_times"] = await self._get_response_time_metrics()
            
            # Throughput metrics
            metrics["throughput"] = await self._get_throughput_metrics(db)
            
            # Error rates
            metrics["error_rates"] = await self._get_error_rate_metrics(db)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return {"error": str(e)}
    
    async def _collect_health_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Collect health check metrics"""
        try:
            health = {}
            
            # Database connectivity
            db_health = await self._check_database_health(db)
            health["database"] = db_health
            
            # Redis connectivity
            redis_health = await self._check_redis_health()
            health["redis"] = redis_health
            
            # External services
            external_health = await self._check_external_services()
            health["external"] = external_health
            
            # Overall health score
            health["overall_score"] = self._calculate_health_score(health)
            
            return health
            
        except Exception as e:
            logger.error(f"Error collecting health metrics: {e}")
            return {"error": str(e)}
    
    async def _get_table_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get table statistics"""
        try:
            query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            return {
                "tables": [
                    {
                        "table": row.tablename,
                        "live_tuples": row.live_tuples,
                        "dead_tuples": row.dead_tuples,
                        "inserts": row.inserts,
                        "updates": row.updates,
                        "deletes": row.deletes
                    }
                    for row in rows
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting table statistics: {e}")
            return {}
    
    async def _get_query_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get query performance statistics"""
        try:
            query = text("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(mean_time) as avg_time,
                    MAX(mean_time) as max_time,
                    MIN(mean_time) as min_time,
                    SUM(calls) as total_calls
                FROM pg_stat_statements
            """)
            
            result = await db.execute(query)
            row = result.fetchone()
            
            return {
                "total_queries": row.total_queries,
                "avg_time_ms": row.avg_time,
                "max_time_ms": row.max_time,
                "min_time_ms": row.min_time,
                "total_calls": row.total_calls
            }
            
        except Exception as e:
            logger.error(f"Error getting query statistics: {e}")
            return {}
    
    async def _get_response_time_metrics(self) -> Dict[str, Any]:
        """Get response time metrics"""
        try:
            # This would typically come from a metrics store
            # For now, return mock data
            return {
                "avg_response_time_ms": 150,
                "p95_response_time_ms": 300,
                "p99_response_time_ms": 500,
                "max_response_time_ms": 1000
            }
            
        except Exception as e:
            logger.error(f"Error getting response time metrics: {e}")
            return {}
    
    async def _get_throughput_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get throughput metrics"""
        try:
            # Get requests per minute
            query = text("""
                SELECT 
                    COUNT(*) as requests_per_minute
                FROM sessions 
                WHERE created_at > NOW() - INTERVAL '1 minute'
            """)
            
            result = await db.execute(query)
            row = result.fetchone()
            
            return {
                "requests_per_minute": row.requests_per_minute,
                "requests_per_hour": row.requests_per_minute * 60,
                "requests_per_day": row.requests_per_minute * 60 * 24
            }
            
        except Exception as e:
            logger.error(f"Error getting throughput metrics: {e}")
            return {}
    
    async def _get_error_rate_metrics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get error rate metrics"""
        try:
            # Get error rates from logs or database
            query = text("""
                SELECT 
                    COUNT(*) as total_requests,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_requests
                FROM sessions 
                WHERE created_at > NOW() - INTERVAL '1 hour'
            """)
            
            result = await db.execute(query)
            row = result.fetchone()
            
            error_rate = (row.failed_requests / row.total_requests * 100) if row.total_requests > 0 else 0
            
            return {
                "total_requests": row.total_requests,
                "failed_requests": row.failed_requests,
                "error_rate_percent": error_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting error rate metrics: {e}")
            return {}
    
    async def _check_database_health(self, db: AsyncSession) -> Dict[str, Any]:
        """Check database health"""
        try:
            start_time = time.time()
            
            # Test database connection
            await db.execute(text("SELECT 1"))
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "connection_count": db.bind.pool.checkedout(),
                "max_connections": db.bind.pool.size()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            # This would check Redis connectivity
            # For now, return mock data
            return {
                "status": "healthy",
                "response_time_ms": 5,
                "memory_usage": "50MB"
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_external_services(self) -> Dict[str, Any]:
        """Check external services health"""
        try:
            services = {}
            
            # Check GoHighLevel API
            ghl_health = await self._check_ghl_api()
            services["go_high_level"] = ghl_health
            
            # Check Google Maps API
            maps_health = await self._check_google_maps_api()
            services["google_maps"] = maps_health
            
            # Check SendGrid API
            sendgrid_health = await self._check_sendgrid_api()
            services["sendgrid"] = sendgrid_health
            
            return services
            
        except Exception as e:
            logger.error(f"Error checking external services: {e}")
            return {"error": str(e)}
    
    async def _check_ghl_api(self) -> Dict[str, Any]:
        """Check GoHighLevel API health"""
        try:
            if not settings.GHL_API_KEY:
                return {"status": "not_configured"}
            
            # Mock health check
            return {
                "status": "healthy",
                "response_time_ms": 200
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_google_maps_api(self) -> Dict[str, Any]:
        """Check Google Maps API health"""
        try:
            if not settings.GOOGLE_MAPS_API_KEY:
                return {"status": "not_configured"}
            
            # Mock health check
            return {
                "status": "healthy",
                "response_time_ms": 100
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_sendgrid_api(self) -> Dict[str, Any]:
        """Check SendGrid API health"""
        try:
            if not settings.SENDGRID_API_KEY:
                return {"status": "not_configured"}
            
            # Mock health check
            return {
                "status": "healthy",
                "response_time_ms": 150
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _calculate_health_score(self, health_metrics: Dict[str, Any]) -> float:
        """Calculate overall health score"""
        try:
            scores = []
            
            # Database health score
            if "database" in health_metrics:
                db_health = health_metrics["database"]
                if db_health.get("status") == "healthy":
                    scores.append(1.0)
                else:
                    scores.append(0.0)
            
            # Redis health score
            if "redis" in health_metrics:
                redis_health = health_metrics["redis"]
                if redis_health.get("status") == "healthy":
                    scores.append(1.0)
                else:
                    scores.append(0.0)
            
            # External services health score
            if "external" in health_metrics:
                external_health = health_metrics["external"]
                service_scores = []
                for service, health in external_health.items():
                    if health.get("status") == "healthy":
                        service_scores.append(1.0)
                    elif health.get("status") == "not_configured":
                        service_scores.append(0.5)  # Partial score for not configured
                    else:
                        service_scores.append(0.0)
                
                if service_scores:
                    scores.append(sum(service_scores) / len(service_scores))
            
            # Calculate overall score
            if scores:
                overall_score = sum(scores) / len(scores)
                return round(overall_score * 100, 2)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 0.0
    
    async def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        try:
            alerts = []
            
            # Check response time
            if "performance" in metrics and "response_times" in metrics["performance"]:
                response_times = metrics["performance"]["response_times"]
                avg_time = response_times.get("avg_response_time_ms", 0)
                if avg_time > self.performance_thresholds["response_time_ms"]:
                    alerts.append({
                        "type": "high_response_time",
                        "severity": "warning",
                        "message": f"Average response time {avg_time}ms exceeds threshold",
                        "value": avg_time,
                        "threshold": self.performance_thresholds["response_time_ms"]
                    })
            
            # Check error rate
            if "performance" in metrics and "error_rates" in metrics["performance"]:
                error_rates = metrics["performance"]["error_rates"]
                error_rate = error_rates.get("error_rate_percent", 0)
                if error_rate > self.performance_thresholds["error_rate_percent"]:
                    alerts.append({
                        "type": "high_error_rate",
                        "severity": "critical",
                        "message": f"Error rate {error_rate}% exceeds threshold",
                        "value": error_rate,
                        "threshold": self.performance_thresholds["error_rate_percent"]
                    })
            
            # Check memory usage
            if "application" in metrics and "memory" in metrics["application"]:
                memory = metrics["application"]["memory"]
                memory_percent = memory.get("percent", 0)
                if memory_percent > self.performance_thresholds["memory_usage_percent"]:
                    alerts.append({
                        "type": "high_memory_usage",
                        "severity": "warning",
                        "message": f"Memory usage {memory_percent}% exceeds threshold",
                        "value": memory_percent,
                        "threshold": self.performance_thresholds["memory_usage_percent"]
                    })
            
            # Check database connections
            if "database" in metrics and "connection_pool" in metrics["database"]:
                pool = metrics["database"]["connection_pool"]
                checked_out = pool.get("checked_out", 0)
                pool_size = pool.get("size", 1)
                connection_percent = (checked_out / pool_size) * 100
                if connection_percent > self.performance_thresholds["database_connections"]:
                    alerts.append({
                        "type": "high_database_connections",
                        "severity": "warning",
                        "message": f"Database connections {connection_percent}% exceeds threshold",
                        "value": connection_percent,
                        "threshold": self.performance_thresholds["database_connections"]
                    })
            
            # Check health score
            if "health" in metrics and "overall_score" in metrics["health"]:
                health_score = metrics["health"]["overall_score"]
                if health_score < 80:
                    alerts.append({
                        "type": "low_health_score",
                        "severity": "critical",
                        "message": f"Overall health score {health_score}% is below threshold",
                        "value": health_score,
                        "threshold": 80
                    })
            
            self.alerts = alerts
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            return []
    
    async def send_alert_notification(self, alert: Dict[str, Any]) -> bool:
        """Send alert notification"""
        try:
            # This would integrate with notification services
            # For now, just log the alert
            logger.warning(f"ALERT: {alert['type']} - {alert['message']}")
            
            # In a real implementation, you would:
            # 1. Send email notifications
            # 2. Send Slack notifications
            # 3. Send SMS alerts
            # 4. Create incident tickets
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
            return False
    
    async def generate_health_report(self, db: AsyncSession) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        try:
            # Collect metrics
            metrics = await self.collect_system_metrics(db)
            
            # Check alerts
            alerts = await self.check_alerts(metrics)
            
            # Generate report
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "alerts": alerts,
                "summary": {
                    "total_alerts": len(alerts),
                    "critical_alerts": len([a for a in alerts if a.get("severity") == "critical"]),
                    "warning_alerts": len([a for a in alerts if a.get("severity") == "warning"]),
                    "overall_health_score": metrics.get("health", {}).get("overall_score", 0)
                }
            }
            
            logger.info(f"Health report generated: {report['summary']}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating health report: {e}")
            return {"error": str(e)}
