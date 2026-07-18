import json
import uuid
import structlog
from typing import Dict, Any
from sentinel_api.ai.schemas.models import ExecutionContext, IncidentContext
from sentinel_api.ai.workflows.executor import WorkflowExecutor
from sentinel_api.services.telemetry_pipeline import redis_conn
from sentinel_api.database.session import AsyncSessionLocal
from sqlalchemy import select
from sentinel_api.models.incident import Incident

logger = structlog.get_logger("sentinel_api.services.integration_trigger")


class IntegrationTriggerService:
    """Handles dispatching incidents to the AI orchestrator and real-time streams."""

    @staticmethod
    async def trigger_workflow(incident_id: str, project_id: str, workspace_id: str):
        """Immediately triggers the LangGraph orchestration and streams the event."""
        logger.info(f"Triggering LangGraph orchestration for incident {incident_id}")
        
        # 1. Fetch incident details
        async with AsyncSessionLocal() as db:
            stmt = select(Incident).where(Incident.id == uuid.UUID(incident_id))
            result = await db.execute(stmt)
            incident = result.scalar_one_or_none()
            
            if not incident:
                logger.error(f"Cannot trigger workflow, incident {incident_id} not found.")
                return

            incident_ctx_data = {
                "incident_id": str(incident.id),
                "severity": incident.severity,
                "status": incident.status,
                "summary": incident.summary or "Unknown anomaly",
                "signals": {}
            }

        # 2. Build AI Contexts
        exec_context = ExecutionContext(
            request_id=f"req-{uuid.uuid4()}",
            correlation_id=f"corr-{uuid.uuid4()}",
            agent_id="system-detector"
        )
        
        incident_context = IncidentContext(**incident_ctx_data)

        # 3. Trigger LangGraph Orchestrator asynchronously
        try:
            executor = WorkflowExecutor()
            # Await the start (it internally delegates graph processing)
            await executor.start(
                incident=incident_context,
                execution_context=exec_context
            )
        except Exception as e:
            logger.exception("Failed to trigger LangGraph workflow", error=str(e))

        # 4. Publish real-time events to Redis for frontend dashboards
        IntegrationTriggerService.publish_event(workspace_id, "Incident Created", incident_ctx_data)

    @staticmethod
    def publish_event(workspace_id: str, event_type: str, data: Dict[str, Any]):
        """Publish lifecycle events to the Redis stream."""
        pubsub_message = {
            "workspace_id": workspace_id,
            "event_type": event_type,
            "data": data
        }
        redis_conn.publish(f"telemetry_stream:{workspace_id}", json.dumps(pubsub_message))
        logger.debug("Published real-time event", event=event_type)
