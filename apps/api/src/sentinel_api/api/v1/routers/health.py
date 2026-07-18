import structlog
from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sentinel_api.database.session import AsyncSessionLocal
from sentinel_api.services.telemetry_pipeline import redis_conn

router = APIRouter(prefix="/health", tags=["health"])
logger = structlog.get_logger("sentinel_api.api.health")

@router.get("")
async def legacy_health():
    return {"status": "healthy", "version": "1.0.0"}

@router.get("/liveness")
async def liveness_probe():
    """
    Indicates whether the application is running. 
    If this fails, Kubernetes will restart the pod.
    """
    return {"status": "ok"}

@router.get("/readiness")
async def readiness_probe(response: Response):
    """
    Indicates whether the application is ready to receive traffic.
    Checks underlying dependencies (PostgreSQL, Redis).
    If this fails, Kubernetes will remove the pod from the Service load balancer.
    """
    health = {
        "status": "ready",
        "database": "unknown",
        "redis": "unknown"
    }
    
    # 1. Check PostgreSQL
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        health["database"] = "up"
    except Exception as e:
        health["database"] = "down"
        health["status"] = "not_ready"
        logger.error("Readiness check failed for PostgreSQL", error=str(e))
        
    # 2. Check Redis
    try:
        if redis_conn.ping():
            health["redis"] = "up"
        else:
            raise Exception("Redis ping returned false")
    except Exception as e:
        health["redis"] = "down"
        health["status"] = "not_ready"
        logger.error("Readiness check failed for Redis", error=str(e))
        
    if health["status"] != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
    return health
