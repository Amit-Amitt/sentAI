from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.controllers.reports import ReportsController
from sentinel_api.api.v1.dependencies.services import get_investigation_service
from sentinel_api.database.session import get_db_session
from sentinel_api.services.investigation import InvestigationService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_controller(
    service: InvestigationService = Depends(get_investigation_service),
) -> ReportsController:
    """Dependency helper instantiating ReportsController."""
    return ReportsController(service)


@router.get("/{incident_id}", response_model=dict)
async def get_report(
    incident_id: str,
    db: AsyncSession = Depends(get_db_session),
    controller: ReportsController = Depends(get_controller),
) -> dict:
    """Returns the unified Incident Report matching incident_id or UUID."""
    return await controller.get_report(db, incident_id)
