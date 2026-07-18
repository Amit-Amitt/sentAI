from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from sentinel_api.database.session import get_db_session
from sentinel_api.services.telemetry_pipeline import AuthCache, TelemetryPipeline
from sentinel_api.api.v1.validators.telemetry import (
    TelemetryBatchRequest,
    LogBatchRequest,
    MetricBatchRequest,
    EventBatchRequest,
    ExceptionBatchRequest,
    HeartbeatBatchRequest,
    DeploymentBatchRequest,
    HealthBatchRequest,
    HeartbeatPayload
)

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

async def verify_api_key(
    x_api_key: str = Header(..., description="Project API Key"),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, str]:
    return await AuthCache.verify_key(x_api_key, db)

@router.post("/batch")
async def ingest_batch(
    payload: TelemetryBatchRequest,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    job_id = TelemetryPipeline.enqueue(
        payload_type="batch",
        project_id=auth['project_id'],
        workspace_id=auth['workspace_id'],
        data=[ev.model_dump() for ev in payload.events]
    )
    return {"success": True, "job_id": job_id}

@router.post("/logs")
async def ingest_logs(
    payload: LogBatchRequest,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    job_id = TelemetryPipeline.enqueue(
        payload_type="logs",
        project_id=auth['project_id'],
        workspace_id=auth['workspace_id'],
        data=[log.model_dump() for log in payload.logs]
    )
    return {"success": True, "job_id": job_id}

@router.post("/metrics")
async def ingest_metrics(
    payload: MetricBatchRequest,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    job_id = TelemetryPipeline.enqueue(
        payload_type="metrics",
        project_id=auth['project_id'],
        workspace_id=auth['workspace_id'],
        data=[met.model_dump() for met in payload.metrics]
    )
    return {"success": True, "job_id": job_id}

@router.post("/events")
async def ingest_events(
    payload: EventBatchRequest,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    job_id = TelemetryPipeline.enqueue(
        payload_type="events",
        project_id=auth['project_id'],
        workspace_id=auth['workspace_id'],
        data=[ev.model_dump() for ev in payload.events]
    )
    return {"success": True, "job_id": job_id}

@router.post("/exceptions")
async def ingest_exceptions(
    payload: ExceptionBatchRequest,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    job_id = TelemetryPipeline.enqueue(
        payload_type="exceptions",
        project_id=auth['project_id'],
        workspace_id=auth['workspace_id'],
        data=[ex.model_dump() for ex in payload.exceptions]
    )
    return {"success": True, "job_id": job_id}

@router.post("/heartbeat")
async def ingest_heartbeat(
    payload: HeartbeatPayload,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    # Backward compat with single payload
    job_id = TelemetryPipeline.enqueue(
        payload_type="heartbeats",
        project_id=auth['project_id'],
        workspace_id=auth['workspace_id'],
        data=[payload.model_dump()]
    )
    return {"success": True, "job_id": job_id}

@router.post("/deployments")
async def ingest_deployments(
    payload: DeploymentBatchRequest,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    job_id = TelemetryPipeline.enqueue(
        payload_type="deployments",
        project_id=auth['project_id'],
        workspace_id=auth['workspace_id'],
        data=[dep.model_dump() for dep in payload.deployments]
    )
    return {"success": True, "job_id": job_id}

@router.post("/health")
async def ingest_health(
    payload: HealthBatchRequest,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    job_id = TelemetryPipeline.enqueue(
        payload_type="health",
        project_id=auth['project_id'],
        workspace_id=auth['workspace_id'],
        data=[hc.model_dump() for hc in payload.health_checks]
    )
    return {"success": True, "job_id": job_id}

@router.get("/stats")
async def get_stats():
    """
    Internal observability endpoint to track queue length and worker health.
    """
    from rq import Queue
    from sentinel_api.services.telemetry_pipeline import redis_conn
    
    q = Queue('telemetry_ingestion', connection=redis_conn)
    return {
        "queue_length": len(q),
        "status": "healthy"
    }
