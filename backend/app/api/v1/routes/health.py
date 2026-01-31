"""
Routes pour le health check de l'API
"""
from fastapi import APIRouter, Depends
from app.db.mongo import get_database
from app.core.redis_cache import redis_cache
from app.core.celery_app import celery_app
from app.core.logger import get_logger

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check basique"""
    return {
        "status": "healthy",
        "service": "SmartScribe API"
    }

@router.get("/detailed")
async def detailed_health_check():
    """Health check détaillé avec vérification des dépendances"""
    health_status = {
        "status": "healthy",
        "service": "SmartScribe API",
        "checks": {}
    }
    
    # Vérification MongoDB
    try:
        db = get_database()
        await db.command("ping")
        health_status["checks"]["mongodb"] = "healthy"
    except Exception as e:
        health_status["checks"]["mongodb"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Vérification Redis
    try:
        await redis_cache.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Vérification Celery
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            health_status["checks"]["celery"] = "healthy"
        else:
            health_status["checks"]["celery"] = "no_workers"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["celery"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
