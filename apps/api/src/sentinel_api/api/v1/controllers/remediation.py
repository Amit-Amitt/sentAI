from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.services.remediation import RemediationService


class RemediationController:
    def __init__(self, service: RemediationService):
        self.service = service

    async def list_remediations(self, db: AsyncSession, workspace_id: str) -> List[Dict[str, Any]]:
        runs = await self.service.list_remediations(db, workspace_id)
        return [
            {
                "id": run.id,
                "incident_id": run.incident_id,
                "status": run.status,
                "created_at": run.created_at.isoformat() if run.created_at else None,
            }
            for run in runs
        ]

    async def get_remediation(self, db: AsyncSession, workspace_id: str, incident_id: str) -> Dict[str, Any]:
        run = await self.service.get_remediation(db, workspace_id, incident_id)
        if not run:
            raise HTTPException(status_code=404, detail="Remediation not found")
        
        return {
            "id": run.id,
            "incident_id": run.incident_id,
            "status": run.status,
            "fix_strategy": run.fix_strategy,
            "code_patch": run.code_patch,
            "github_pr_draft": run.github_pr_draft,
            "rollback_plan": run.rollback_plan,
            "risk_analysis": run.risk_analysis,
            "runbook": run.runbook,
            "created_at": run.created_at.isoformat() if run.created_at else None,
        }

    async def generate_remediation(self, db: AsyncSession, workspace_id: str, incident_id: str) -> Dict[str, Any]:
        try:
            run = await self.service.generate_remediation(db, workspace_id, incident_id)
            return {
                "id": run.id,
                "incident_id": run.incident_id,
                "status": run.status,
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate remediation: {e}")
