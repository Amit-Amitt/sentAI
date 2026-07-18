import structlog
import uuid
import datetime
from typing import Dict, Any, List
from sqlalchemy import select
from sentinel_api.database.session import AsyncSessionLocal
from sentinel_api.models.notifications import NotificationPolicy, NotificationChannel, NotificationHistory
from sentinel_api.models.incident import Incident
from sentinel_api.services.telemetry_pipeline import telemetry_queue

logger = structlog.get_logger("sentinel_api.services.notification_engine")

class NotificationEngine:
    """Orchestrates routing incidents to appropriate notification channels based on policies."""

    @staticmethod
    async def route_incident(incident_id: str):
        """
        Called when an incident is created or updated. 
        Evaluates active policies and enqueues delivery tasks.
        """
        async with AsyncSessionLocal() as db:
            incident = await db.get(Incident, uuid.UUID(incident_id))
            if not incident:
                logger.error("Incident not found for routing", incident_id=incident_id)
                return

            # Fetch active policies for the workspace
            stmt_policies = select(NotificationPolicy).where(
                NotificationPolicy.project_id == incident.project_id,
                NotificationPolicy.is_active == True
            )
            res = await db.execute(stmt_policies)
            policies = res.scalars().all()
            
            dispatched_channels = set()
            
            for policy in policies:
                # Basic rule evaluation (e.g. severity match)
                rules = policy.rules
                target_severities = rules.get("severity", [])
                
                if target_severities and incident.severity not in target_severities:
                    continue
                    
                if policy.channel_id in dispatched_channels:
                    continue # Prevent duplicate notifications to same channel
                
                dispatched_channels.add(policy.channel_id)
                
                # Create history record
                history = NotificationHistory(
                    id=uuid.uuid4(),
                    incident_id=incident.id,
                    channel_id=policy.channel_id,
                    status="pending"
                )
                db.add(history)
                await db.flush()
                
                # In a real system, we might ask the LLM to generate an "AI Briefing" here 
                # before enqueuing.
                
                # Enqueue the actual HTTP delivery to background worker
                telemetry_queue.enqueue(
                    "sentinel_api.workers.notification_tasks.deliver_notification",
                    history_id=str(history.id)
                )
                
            await db.commit()
