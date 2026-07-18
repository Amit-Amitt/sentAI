from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.controllers.incidents import IncidentsController
from sentinel_api.api.v1.dependencies.services import get_investigation_service
from sentinel_api.api.v1.responses.schemas import (
    AnalysisSubmitResponse,
    DeleteResponse,
    InvestigationListResponse,
)
from sentinel_api.api.v1.validators.schemas import IncidentAnalyzeRequest
from sentinel_api.database.session import get_db_session
from sentinel_api.services.investigation import InvestigationService

router = APIRouter(prefix="/incidents", tags=["incidents"])


def get_controller(
    service: InvestigationService = Depends(get_investigation_service),
) -> IncidentsController:
    """Dependency injection helper retrieving IncidentsController."""
    return IncidentsController(service)


@router.post("/analyze", response_model=AnalysisSubmitResponse, status_code=202)
async def analyze_incident(
    payload: IncidentAnalyzeRequest,
    db: AsyncSession = Depends(get_db_session),
    controller: IncidentsController = Depends(get_controller),
) -> AnalysisSubmitResponse:
    """Submits and triggers a multi-agent incident analysis run."""
    return await controller.analyze(db, payload)


@router.get("", response_model=InvestigationListResponse)
async def list_investigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db_session),
    controller: IncidentsController = Depends(get_controller),
) -> InvestigationListResponse:
    """Queries paginated records of historical investigation runs."""
    return await controller.list_all(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{incident_id}", response_model=dict)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db_session),
    controller: IncidentsController = Depends(get_controller),
) -> dict:
    """Returns the compiled incident report matching incident_id or UUID."""
    return await controller.get(db, incident_id)


@router.delete("/{incident_id}", response_model=DeleteResponse)
async def delete_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db_session),
    controller: IncidentsController = Depends(get_controller),
) -> DeleteResponse:
    """Deletes historical investigation record by incident_id or UUID."""
    res = await controller.delete(db, incident_id)
    return DeleteResponse(success=res["success"], message=res["message"])
