import uuid
import datetime
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict, Any
from sentinel_api.database.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel_api.services.telemetry_pipeline import telemetry_queue

router = APIRouter(prefix="/observability", tags=["observability"])

@router.post("/alertmanager/webhook")
async def alertmanager_webhook(
    request: Request,
    project_id: str,
    workspace_id: str
):
    """Receive webhooks from Prometheus Alertmanager."""
    
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    alerts = payload.get("alerts", [])
    
    # We map Alertmanager alerts to Sentinel AI "events" or "exceptions"
    # and push them into the standard telemetry pipeline. 
    # This allows the Sentinel DetectionEngine to automatically correlate them.
    for alert in alerts:
        status = alert.get("status") # firing or resolved
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        
        # Determine severity mapping
        severity = labels.get("severity", "error")
        if status == "resolved":
            severity = "info"
            
        telemetry_event = {
            "type": "event",
            "name": labels.get("alertname", "Alertmanager Alert"),
            "level": severity,
            "message": annotations.get("description", annotations.get("summary", "")),
            "timestamp": alert.get("startsAt"),
            "resource_attributes": labels,
            "observability_source": "alertmanager"
        }
        
        # Enqueue to existing Telemetry Pipeline
        telemetry_queue.enqueue(
            "sentinel_api.workers.telemetry_tasks.process_telemetry_batch",
            project_id=project_id,
            workspace_id=workspace_id,
            payload_type="events",
            items=[telemetry_event],
            api_key_id=None
        )

    return {"success": True, "processed": len(alerts)}
