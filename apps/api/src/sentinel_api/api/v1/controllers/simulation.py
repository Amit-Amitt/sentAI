from typing import List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.services.simulation import SimulationService, SimulationLibrary
from sentinel_api.models.simulation import SimulationRun
from pydantic import BaseModel

class StartSimulationRequest(BaseModel):
    scenario_id: str
    severity: str

class SimulationController:
    def __init__(self, service: SimulationService):
        self.service = service

    async def get_scenarios(self) -> List[Dict[str, Any]]:
        return SimulationLibrary.SCENARIOS

    async def get_history(self, db: AsyncSession, workspace_id: str) -> List[dict]:
        runs = await self.service.get_history(db, workspace_id)
        return [
            {
                "id": run.id,
                "incident_id": run.incident_id,
                "scenario_id": run.scenario_id,
                "severity": run.severity,
                "status": run.status,
                "created_at": run.created_at.isoformat() if run.created_at else None,
            }
            for run in runs
        ]

    async def start_simulation(self, db: AsyncSession, workspace_id: str, payload: StartSimulationRequest) -> dict:
        try:
            run_record = await self.service.start_simulation(
                db=db,
                workspace_id=workspace_id,
                scenario_id=payload.scenario_id,
                severity=payload.severity
            )
            return {
                "id": run_record.id,
                "incident_id": run_record.incident_id,
                "scenario_id": run_record.scenario_id,
                "status": run_record.status,
                "severity": run_record.severity,
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start simulation: {e}")
