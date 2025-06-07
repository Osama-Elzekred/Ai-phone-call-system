"""
Health check endpoints for AI Hotline Backend.
Provides multiple health check endpoints for different use cases.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.ai_hotline.shared.health import health_checker
from src.ai_hotline.shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", summary="Basic health check", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint for load balancers and simple monitoring.
    
    Returns a quick status check without detailed diagnostics.
    This endpoint should be lightweight and fast.
    """
    try:
        result = await health_checker.basic_health_check()
        return result
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": "Health check failed",
                "message": str(e)
            }
        )


@router.get("/health/detailed", summary="Detailed health check", tags=["Health"])
async def detailed_health_check():
    """
    Comprehensive health check with detailed diagnostics.
    
    Checks all system dependencies including:
    - Database connectivity
    - Redis connectivity (if configured)
    - External API availability
    - System resources
    
    Use this endpoint for monitoring dashboards and debugging.
    """
    try:
        result = await health_checker.detailed_health_check()
        
        # Return appropriate HTTP status based on health
        if result["status"] == "unhealthy":
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=result
            )
        
        return result
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": "Detailed health check failed",
                "message": str(e)
            }
        )


@router.get("/health/ready", summary="Readiness check", tags=["Health"])
async def readiness_check():
    """
    Kubernetes-style readiness probe.
    
    Checks if the application is ready to serve requests.
    This differs from liveness in that it checks if dependencies
    are available and the app can handle traffic.
    
    Returns:
    - 200: Ready to serve requests
    - 503: Not ready (dependencies unavailable)
    """
    try:
        result = await health_checker.readiness_check()
        
        if not result.get("ready", False):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=result
            )
        
        return result
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "error": "Readiness check failed",
                "message": str(e)
            }
        )


@router.get("/health/live", summary="Liveness check", tags=["Health"])
async def liveness_check():
    """
    Kubernetes-style liveness probe.
    
    Simple check to verify the application is running and responsive.
    This should only fail if the application process itself is broken.
    
    Returns:
    - 200: Application is alive
    - 503: Application is dead (should be restarted)
    """
    try:
        # Simple liveness check - just verify the app is responding
        result = await health_checker.basic_health_check()
        return {
            "status": "alive",
            "timestamp": result["timestamp"],
            "service": result["service"]
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "dead",
                "error": "Liveness check failed",
                "message": str(e)
            }
        )
