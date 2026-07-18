import redis
from rq import Queue
import time
from typing import Dict, Any, List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sentinel_api.config.settings import settings
from sentinel_api.models.project import Project

redis_conn = redis.from_url(settings.REDIS_URL)
telemetry_queue = Queue('telemetry_ingestion', connection=redis_conn)

class RateLimiter:
    """Token bucket rate limiter using Redis"""
    
    @staticmethod
    def is_allowed(project_id: str, limit: int = 100000, window: int = 60) -> bool:
        key = f"rate_limit:telemetry:{project_id}"
        current = redis_conn.get(key)
        
        if current and int(current) >= limit:
            return False
            
        pipe = redis_conn.pipeline()
        pipe.incr(key)
        pipe.expire(key, window, nx=True)
        pipe.execute()
        return True

class AuthCache:
    """Caches Project API Key lookups in Redis for 5 minutes"""
    
    @staticmethod
    async def verify_key(api_key: str, db: AsyncSession) -> Dict[str, str]:
        cache_key = f"auth:apikey:{api_key}"
        cached = redis_conn.hgetall(cache_key)
        
        if cached:
            return {k.decode('utf-8'): v.decode('utf-8') for k, v in cached.items()}
            
        stmt = select(Project).where(Project.api_key == api_key)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=401, detail="Invalid Project API Key")
            
        data = {
            "project_id": str(project.id),
            "workspace_id": str(project.workspace_id)
        }
        
        redis_conn.hmset(cache_key, data)
        redis_conn.expire(cache_key, 300) # Cache for 5 minutes
        
        return data

class TelemetryPipeline:
    
    @staticmethod
    def enqueue(payload_type: str, project_id: str, workspace_id: str, data: List[Dict[str, Any]]):
        """Validates rate limits and pushes to RQ"""
        if not RateLimiter.is_allowed(project_id):
            raise HTTPException(status_code=429, detail="Too Many Requests")
            
        # Pushing to background worker
        job = telemetry_queue.enqueue(
            'sentinel_api.workers.telemetry_tasks.process_telemetry_batch',
            kwargs={
                'payload_type': payload_type,
                'project_id': project_id,
                'workspace_id': workspace_id,
                'data': data
            }
        )
        return job.id
