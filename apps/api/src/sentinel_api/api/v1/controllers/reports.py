import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.services.investigation import InvestigationService


class ReportsController:
    """Controller returning the unified Incident Report."""

    def __init__(self, service: InvestigationService) -> None:
        self.service = service

    async def get_report(self, db: AsyncSession, incident_id: str) -> dict:
        """Retrieves and returns the generated incident report section."""
        try:
            inv_id = uuid.UUID(incident_id)
            inv = await self.service.get_investigation(db, inv_id)
        except ValueError:
            invs = await self.service.list_investigations(
                db, limit=1000, status=None
            )
            inv = next((x for x in invs if x.incident_id == incident_id), None)

        if not inv:
            raise HTTPException(
                status_code=404,
                detail=f"Incident investigation not found: {incident_id}",
            )
        return inv.incident_report
