import uuid
import structlog
from typing import Dict, Any, Optional
from sentinel_api.database.session import AsyncSessionLocal
from sentinel_api.models.iam import AuditLog

logger = structlog.get_logger("sentinel_api.services.audit_service")

class AuditService:
    @staticmethod
    async def log_event(
        action: str,
        status: str, # "success" or "failure"
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
        service_account_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """Asynchronously insert an immutable audit log record."""
        try:
            async with AsyncSessionLocal() as db:
                log = AuditLog(
                    id=uuid.uuid4(),
                    action=action,
                    status=status,
                    organization_id=uuid.UUID(organization_id) if organization_id else None,
                    user_id=uuid.UUID(user_id) if user_id else None,
                    service_account_id=uuid.UUID(service_account_id) if service_account_id else None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata_json=metadata or {}
                )
                db.add(log)
                await db.commit()
        except Exception as e:
            # We don't want an audit logging failure to crash the main request loop,
            # but we absolutely must log it loudly.
            logger.error("CRITICAL: Failed to write AuditLog", action=action, error=str(e))
