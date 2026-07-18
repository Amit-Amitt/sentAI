from typing import Dict, Any
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.database.session import get_db_session
from sentinel_api.services.telemetry_pipeline import AuthCache, TelemetryPipeline
from sentinel_api.services.otlp_parser import OTLPParser

router = APIRouter(prefix="/otlp/v1", tags=["otlp"])

async def verify_api_key(
    x_api_key: str = Header(..., description="Project API Key"),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, str]:
    """Verify auth key for OTLP pipeline."""
    return await AuthCache.verify_key(x_api_key, db)

@router.post("/traces")
async def ingest_otlp_traces(
    request: Request,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    """OTLP HTTP Receiver for Traces"""
    payload = await request.json()
    parsed_spans = OTLPParser.parse_traces(payload)
    
    if parsed_spans:
        job_id = TelemetryPipeline.enqueue(
            payload_type="spans",
            project_id=auth['project_id'],
            workspace_id=auth['workspace_id'],
            data=parsed_spans
        )
        return {"success": True, "job_id": job_id}
    return {"success": True, "job_id": None}


@router.post("/metrics")
async def ingest_otlp_metrics(
    request: Request,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    """OTLP HTTP Receiver for Metrics"""
    payload = await request.json()
    parsed_metrics = OTLPParser.parse_metrics(payload)
    
    if parsed_metrics:
        job_id = TelemetryPipeline.enqueue(
            payload_type="metrics",
            project_id=auth['project_id'],
            workspace_id=auth['workspace_id'],
            data=parsed_metrics
        )
        return {"success": True, "job_id": job_id}
    return {"success": True, "job_id": None}


@router.post("/logs")
async def ingest_otlp_logs(
    request: Request,
    auth: Dict[str, str] = Depends(verify_api_key)
):
    """OTLP HTTP Receiver for Logs"""
    payload = await request.json()
    parsed_logs = OTLPParser.parse_logs(payload)
    
    if parsed_logs:
        job_id = TelemetryPipeline.enqueue(
            payload_type="logs",
            project_id=auth['project_id'],
            workspace_id=auth['workspace_id'],
            data=parsed_logs
        )
        return {"success": True, "job_id": job_id}
    return {"success": True, "job_id": None}
