import uuid
from typing import List, Optional
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.remediation import RemediationRun
from sentinel_api.ai.engines.remediation import AutonomousRemediationEngine
from sentinel_api.models.investigation import Investigation
from sentinel_api.services.investigation import InvestigationService

logger = structlog.get_logger("sentinel_api.services.remediation")


class RemediationService:
    def __init__(self):
        self.engine = AutonomousRemediationEngine()
        self.investigation_service = InvestigationService()

    async def list_remediations(self, db: AsyncSession, workspace_id: str) -> List[RemediationRun]:
        stmt = select(RemediationRun).where(RemediationRun.workspace_id == workspace_id).order_by(RemediationRun.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_remediation(self, db: AsyncSession, workspace_id: str, incident_id: str) -> Optional[RemediationRun]:
        stmt = select(RemediationRun).where(
            RemediationRun.workspace_id == workspace_id,
            RemediationRun.incident_id == incident_id
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def generate_remediation(self, db: AsyncSession, workspace_id: str, incident_id: str) -> RemediationRun:
        """Generates an AI Remediation plan for the specified incident."""
        logger.info(f"Generating remediation for incident {incident_id}")
        
        # 1. Fetch Investigation for context
        # In this implementation, the frontend sends the incident_id which maps to Investigation.incident_id
        stmt = select(Investigation).where(Investigation.incident_id == incident_id)
        res = await db.execute(stmt)
        investigation = res.scalar_one_or_none()
        
        if not investigation:
            raise ValueError(f"No investigation found for incident {incident_id}")
            
        summary = investigation.summary or "Unknown incident"
        agent_outputs = investigation.agent_outputs or {}
        root_cause = investigation.incident_report.get("root_cause", {})
        
        # 2. Check if a remediation already exists
        existing = await self.get_remediation(db, workspace_id, incident_id)
        if existing and existing.status == "COMPLETED":
            return existing

        remediation = existing or RemediationRun(
            id=str(uuid.uuid4()).replace("-", ""),
            incident_id=incident_id,
            workspace_id=workspace_id,
            status="GENERATING"
        )
        if not existing:
            db.add(remediation)
            await db.commit()
            
        # 3. Trigger Engine
        try:
            plan = await self.engine.generate_plan(
                incident_summary=summary,
                root_cause=root_cause,
                agent_outputs=agent_outputs
            )
            
            # 4. Save to DB
            remediation.fix_strategy = plan.fix_strategy
            # Add infrastructure_commands to fix_strategy to persist it cleanly
            remediation.fix_strategy.extend(["--- Infrastructure Commands ---"] + plan.infrastructure_commands)
            
            remediation.code_patch = plan.code_patch.model_dump()
            remediation.github_pr_draft = plan.github_pr_draft.model_dump()
            remediation.rollback_plan = plan.rollback_plan.model_dump()
            remediation.risk_analysis = plan.risk_analysis.model_dump()
            remediation.runbook = plan.runbook.model_dump()
            remediation.status = "COMPLETED"
            
            await db.commit()
            await db.refresh(remediation)
            
            return remediation
            
        except Exception as e:
            logger.error(f"Remediation generation failed: {e}")
            remediation.status = "FAILED"
            await db.commit()
            raise RuntimeError(f"Remediation generation failed: {e}")
