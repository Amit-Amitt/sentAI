import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import time

from sentinel_api.database.session import get_db_session
from sentinel_api.api.v1.dependencies.security import get_current_user_jwt
from sentinel_api.services.telemetry_pipeline import telemetry_queue
from sentinel_api.config.settings import settings

router = APIRouter(prefix="/demo", tags=["demo"])
logger = structlog.get_logger("sentinel_api.api.demo")

class FaultInjectionRequest(BaseModel):
    project_id: str
    scenario: str # e.g. "db_latency", "redis_oom", "github_bad_deploy"

def _generate_db_latency_payloads() -> List[Dict[str, Any]]:
    now = int(time.time() * 1000)
    return [
        {
            "timestamp": now,
            "metric_name": "db.query.latency",
            "value": 1450.5, # 1.4s latency
            "labels": {"service": "postgres", "pool": "primary"},
            "type": "metric"
        },
        {
            "timestamp": now,
            "message": "Timeout acquiring connection from pool",
            "level": "error",
            "service": "api-gateway",
            "type": "log"
        }
    ]

def _generate_redis_oom_payloads() -> List[Dict[str, Any]]:
    now = int(time.time() * 1000)
    return [
        {
            "timestamp": now,
            "metric_name": "redis.memory.usage",
            "value": 105.2, # 105% (over limit)
            "labels": {"service": "redis", "cluster": "cache"},
            "type": "metric"
        },
        {
            "timestamp": now,
            "message": "OOM command not allowed when used memory > 'maxmemory'",
            "level": "critical",
            "service": "redis",
            "type": "log"
        }
    ]

@router.post("/inject-fault")
async def inject_fault(
    payload: FaultInjectionRequest,
    current_user: dict = Depends(get_current_user_jwt),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Simulates a production outage by injecting synthetic telemetry payloads 
    directly into the Telemetry Pipeline, triggering existing detection rules 
    and AI LangGraph agents naturally.
    """
    # In a real SaaS we would aggressively restrict this, 
    # but for Hackathon Demo Mode it is essential.
    
    workspace_id = current_user.get("workspace_id", "00000000-0000-0000-0000-000000000000")
    
    logger.info("Injecting synthetic fault", scenario=payload.scenario, project=payload.project_id)
    
    telemetry_payloads = []
    
    if payload.scenario == "db_latency":
        telemetry_payloads = _generate_db_latency_payloads()
    elif payload.scenario == "redis_oom":
        telemetry_payloads = _generate_redis_oom_payloads()
    else:
        raise HTTPException(status_code=400, detail="Unknown scenario")
        
    # Inject directly into the async telemetry queue
    job = telemetry_queue.enqueue(
        'sentinel_api.workers.telemetry_tasks.process_telemetry_batch',
        kwargs={
            'payload_type': 'demo_synthetic',
            'project_id': payload.project_id,
            'workspace_id': workspace_id,
            'data': telemetry_payloads
        }
    )
    
    return {
        "status": "success", 
        "message": f"Injected synthetic {payload.scenario} telemetry",
        "job_id": job.id
    }
