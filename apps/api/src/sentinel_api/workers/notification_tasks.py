import uuid
import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from sentinel_api.database.session import engine
from sentinel_api.models.notifications import NotificationHistory, NotificationChannel
from sentinel_api.models.incident import Incident
from sentinel_api.services.notification_providers import get_provider

logger = structlog.get_logger("sentinel_api.workers.notification_tasks")

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def _deliver_notification_async(history_id: str):
    """Attempt to deliver a notification. Updates history on success or failure."""
    async with AsyncSessionLocal() as db:
        stmt = select(NotificationHistory).where(NotificationHistory.id == uuid.UUID(history_id))
        result = await db.execute(stmt)
        history = result.scalar_one_or_none()
        
        if not history:
            logger.error("Notification history not found", history_id=history_id)
            return
            
        channel = await db.get(NotificationChannel, history.channel_id)
        incident = await db.get(Incident, history.incident_id)
        
        if not channel or not incident:
            history.status = "failed"
            history.error_message = "Channel or Incident missing"
            await db.commit()
            return
            
        provider = get_provider(channel.provider_type, channel.config)
        
        try:
            # Optionally format an AI Briefing here
            briefing = f"Sentinel AI has detected an anomaly.\n\nSummary: {incident.summary or incident.title}\n\nPlease check the dashboard."
            
            success = await provider.deliver(
                title=f"Incident {incident.incident_key}: {incident.title}",
                message=briefing,
                severity=incident.severity
            )
            
            if success:
                history.status = "delivered"
            else:
                history.status = "failed"
                history.error_message = "Provider returned False"
                history.retry_count += 1
                
        except Exception as e:
            history.status = "failed"
            history.error_message = str(e)
            history.retry_count += 1
            logger.error("Failed to deliver notification", error=str(e))
            
        await db.commit()

def deliver_notification(history_id: str):
    import asyncio
    asyncio.run(_deliver_notification_async(history_id))
