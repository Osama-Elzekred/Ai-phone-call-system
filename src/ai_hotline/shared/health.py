"""
Health check module for AI Hotline Backend.
Provides comprehensive health monitoring for all system dependencies.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional

import asyncpg
import redis.asyncio as redis
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.ai_hotline.shared.config import get_settings
from src.ai_hotline.shared.database import get_db_context
from src.ai_hotline.shared.logging import get_logger

logger = get_logger(__name__)


class HealthChecker:
    """Comprehensive health checker for all system dependencies."""
    
    def __init__(self):
      self.settings = get_settings()
        
    async def check_database(self) -> Dict[str, Any]:
        """Check PostgreSQL database connectivity and basic operations."""
        start_time = time.time()
        try:
            with get_db_context() as session:
                # Test basic connectivity
                result = session.execute(text("SELECT 1 as test"))
                test_value = result.scalar()
                
                # Test database version
                version_result = session.execute(text("SELECT version()"))
                db_version = version_result.scalar()
                
                response_time = time.time() - start_time
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time * 1000, 2),
                    "test_query": test_value == 1,
                    "database_version": db_version.split()[0] if db_version else "unknown",
                    "message": "Database connection successful"
                }
                
        except SQLAlchemyError as e:
            response_time = time.time() - start_time
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time * 1000, 2),
                "error": str(e),
                "message": "Database connection failed"
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Unexpected database health check error: {e}")
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time * 1000, 2),
                "error": str(e),
                "message": "Unexpected database error"
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and basic operations."""
        start_time = time.time()
        
        # Skip Redis check if not configured
        if not hasattr(self.settings, 'redis_url') or not self.settings.redis_url:
            return {
                "status": "skipped",
                "message": "Redis not configured"
            }
        
        try:
            # Create Redis connection
            redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test basic connectivity
            await redis_client.ping()
            
            # Test basic operations
            test_key = "health_check_test"
            test_value = f"test_{int(time.time())}"
            
            await redis_client.set(test_key, test_value, ex=10)  # Expire in 10 seconds
            retrieved_value = await redis_client.get(test_key)
            await redis_client.delete(test_key)
            
            # Get Redis info
            info = await redis_client.info()
            
            await redis_client.close()
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "test_operations": retrieved_value == test_value,
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "message": "Redis connection successful"
            }
            
        except redis.RedisError as e:
            response_time = time.time() - start_time
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time * 1000, 2),
                "error": str(e),
                "message": "Redis connection failed"
            }
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Unexpected Redis health check error: {e}")
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time * 1000, 2),
                "error": str(e),
                "message": "Unexpected Redis error"
            }
    
    async def check_external_apis(self) -> Dict[str, Any]:
        """Check external API connectivity (OpenAI, ElevenLabs, etc.)."""
        start_time = time.time()
        
        checks = {}
        
        # Note: We'll do lightweight checks to avoid hitting rate limits
        # In production, consider using dedicated health endpoints if available
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                
                # Check OpenAI API (if configured)
                if hasattr(self.settings, 'openai_api_key') and self.settings.openai_api_key:
                    try:
                        response = await client.get(
                            "https://api.openai.com/v1/models",
                            headers={"Authorization": f"Bearer {self.settings.openai_api_key}"}
                        )
                        checks["openai"] = {
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "status_code": response.status_code
                        }
                    except Exception as e:
                        checks["openai"] = {
                            "status": "unhealthy",
                            "error": str(e)
                        }
                
                # Check ElevenLabs API (if configured)
                if hasattr(self.settings, 'elevenlabs_api_key') and self.settings.elevenlabs_api_key:
                    try:
                        response = await client.get(
                            "https://api.elevenlabs.io/v1/voices",
                            headers={"xi-api-key": self.settings.elevenlabs_api_key}
                        )
                        checks["elevenlabs"] = {
                            "status": "healthy" if response.status_code == 200 else "unhealthy",
                            "status_code": response.status_code
                        }
                    except Exception as e:
                        checks["elevenlabs"] = {
                            "status": "unhealthy",
                            "error": str(e)
                        }
        
        except ImportError:
            checks["httpx"] = {
                "status": "unavailable",
                "message": "httpx not installed for external API checks"
            }
        
        response_time = time.time() - start_time
        
        return {
            "status": "completed",
            "response_time_ms": round(response_time * 1000, 2),            "checks": checks,
            "message": "External API checks completed"
        }
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        try:
            import psutil
            import platform
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_usage_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2)
                }
            }
        except ImportError:
            logger.warning("psutil not available, system info limited")
            import platform
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "message": "Limited system info (psutil not available)"
            }
        except Exception as e:
            logger.warning(f"Could not get system info: {e}")
            return {
                "error": "System info unavailable",
                "message": str(e)
            }

    async def basic_health_check(self) -> Dict[str, Any]:
        """Quick health check for load balancer probes."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ai-hotline-backend",
            "version": getattr(self.settings, 'version', '1.0.0')
        }
    
    async def detailed_health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for monitoring and debugging."""
        start_time = time.time()
        
        # Run all checks concurrently
        db_check, redis_check, api_check, system_info = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_external_apis(),
            self.get_system_info(),
            return_exceptions=True
        )
        
        total_time = time.time() - start_time
        
        # Determine overall health status
        critical_systems = [db_check]  # Database is critical
        overall_status = "healthy"
        
        for check in critical_systems:
            if isinstance(check, Exception):
                overall_status = "unhealthy"
                break
            elif check.get("status") == "unhealthy":
                overall_status = "unhealthy"
                break
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ai-hotline-backend",
            "version": getattr(self.settings, 'version', '1.0.0'),
            "environment": getattr(self.settings, 'environment', 'unknown'),
            "total_check_time_ms": round(total_time * 1000, 2),
            "checks": {
                "database": db_check if not isinstance(db_check, Exception) else {"status": "error", "error": str(db_check)},
                "redis": redis_check if not isinstance(redis_check, Exception) else {"status": "error", "error": str(redis_check)},
                "external_apis": api_check if not isinstance(api_check, Exception) else {"status": "error", "error": str(api_check)},
                "system": system_info if not isinstance(system_info, Exception) else {"status": "error", "error": str(system_info)}
            }
        }
    
    async def readiness_check(self) -> Dict[str, Any]:
        """Check if the application is ready to serve requests."""
        start_time = time.time()
        
        # Check critical dependencies for readiness
        db_check = await self.check_database()
        
        total_time = time.time() - start_time
        
        is_ready = db_check.get("status") == "healthy"
        
        return {
            "status": "ready" if is_ready else "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ai-hotline-backend",
            "check_time_ms": round(total_time * 1000, 2),
            "ready": is_ready,
            "dependencies": {
                "database": db_check
            }
        }


# Global health checker instance
health_checker = HealthChecker()
