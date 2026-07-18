import uuid
import datetime
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.database.session import get_db_session
from sentinel_api.api.v1.controllers.simulation import SimulationController, StartSimulationRequest
from sentinel_api.services.simulation import SimulationService

router = APIRouter(prefix="/simulation", tags=["simulation"])

service = SimulationService()
controller = SimulationController(service)

@router.get("/scenarios", response_model=List[Dict[str, Any]])
async def list_scenarios():
    """List all available simulation scenarios."""
    return await controller.get_scenarios()

@router.get("/history", response_model=List[Dict[str, Any]])
async def list_history(
    workspace_id: str = Query(..., description="The ID of the active workspace"),
    db: AsyncSession = Depends(get_db_session),
):
    """List historical simulation runs for the workspace."""
    return await controller.get_history(db, workspace_id)

@router.post("/start")
async def start_simulation(
    payload: StartSimulationRequest,
    workspace_id: str = Query(..., description="The ID of the active workspace"),
    db: AsyncSession = Depends(get_db_session),
):
    """Start a new production incident simulation."""
    return await controller.start_simulation(db, workspace_id, payload)

class DemoTriggerRequest(BaseModel):
    type: str
    workspace_id: str

@router.post("/demo-trigger")
async def demo_trigger(
    payload: DemoTriggerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    from sentinel_api.models.project import Project
    from sentinel_api.models.telemetry import TelemetryEvent
    from sentinel_api.services.detection import DetectionEngine
    from sqlalchemy import select
    
    # Check if a project exists for the workspace, if not create a mock one
    stmt = select(Project).where(Project.workspace_id == payload.workspace_id).limit(1)
    res = await db.execute(stmt)
    proj = res.scalar_one_or_none()
    
    if not proj:
        proj = Project(
            id=uuid.uuid4(),
            workspace_id=payload.workspace_id,
            name="demo-production-app",
            api_key=f"sent_demo_{uuid.uuid4().hex}"
        )
        db.add(proj)
        await db.commit()
    
    # Generate 6 errors to trigger the detection engine rule (>5 errors)
    events = []
    for _ in range(6):
        events.append(
            TelemetryEvent(
                id=uuid.uuid4(),
                project_id=proj.id,
                workspace_id=payload.workspace_id,
                event_type="EXCEPTION",
                payload={"message": f"Demo Failure: {payload.type}", "fatal": True},
                timestamp=datetime.datetime.utcnow()
            )
        )
    db.add_all(events)
    await db.commit()
    
    # Run the detection engine
    background_tasks.add_task(DetectionEngine.evaluate_rules, str(proj.id), payload.workspace_id)
    return {"success": True, "message": "Injected telemetry"}
