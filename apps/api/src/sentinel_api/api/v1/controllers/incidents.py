import uuid
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.responses.schemas import (
    AnalysisSubmitResponse,
    InvestigationListResponse,
)
from sentinel_api.api.v1.validators.schemas import IncidentAnalyzeRequest
from sentinel_api.services.investigation import InvestigationService


class IncidentsController:
    """Controller handling routing/mapping logic for incident endpoints."""

    def __init__(self, service: InvestigationService) -> None:
        self.service = service

    async def analyze(
        self, db: AsyncSession, payload: IncidentAnalyzeRequest
    ) -> AnalysisSubmitResponse:
        """Starts a full multi-agent incident analysis run."""
        try:
            inv = await self.service.analyze_incident(
                db=db,
                incident_id=payload.incident_id,
                severity=payload.severity,
                status=payload.status,
                summary=payload.summary,
                logs=payload.logs,
                metrics=payload.metrics,
                deployment_history=payload.deployment_history,
                customer_reports=payload.customer_reports,
            )
            return AnalysisSubmitResponse(
                investigation_id=str(inv.id),
                status=inv.status,
                incident_id=inv.incident_id,
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to submit incident analysis: {e}",
            )

    async def get(self, db: AsyncSession, incident_id: str) -> dict:
        """Returns the full incident report matching incident_id or UUID."""
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

    async def delete(self, db: AsyncSession, incident_id: str) -> dict:
        """Deletes historical investigation matching incident_id or UUID."""
        try:
            inv_id = uuid.UUID(incident_id)
            deleted = await self.service.delete_investigation(db, inv_id)
        except ValueError:
            invs = await self.service.list_investigations(
                db, limit=1000, status=None
            )
            target = next((x for x in invs if x.incident_id == incident_id), None)
            if target:
                deleted = await self.service.delete_investigation(db, target.id)
            else:
                deleted = False

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Incident investigation not found for deletion: {incident_id}",
            )
        return {
            "success": True,
            "message": f"Investigation {incident_id} successfully deleted",
        }

    async def list_all(
        self,
        db: AsyncSession,
        skip: int,
        limit: int,
        status: Optional[str],
        sort_by: str,
        sort_order: str,
    ) -> InvestigationListResponse:
        """Retrieves a paginated list of past investigations."""
        records = await self.service.list_investigations(
            db=db,
            skip=skip,
            limit=limit,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        results = []
        for r in records:
            results.append(
                {
                    "id": str(r.id),
                    "incident_id": r.incident_id,
                    "severity": r.severity,
                    "status": r.status,
                    "summary": r.summary,
                    "created_at": (
                        r.created_at.isoformat() if r.created_at else None
                    ),
                    "updated_at": (
                        r.updated_at.isoformat() if r.updated_at else None
                    ),
                }
            )

        all_records = await self.service.list_investigations(
            db=db, limit=1000, status=status
        )
        total = len(all_records)

        return InvestigationListResponse(
            results=results, total=total, skip=skip, limit=limit
        )
