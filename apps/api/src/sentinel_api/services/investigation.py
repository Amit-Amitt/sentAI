import uuid
from typing import Any, Dict, List, Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.ai.agents.coordinator import CoordinatorAgent
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)
from sentinel_api.app.reporting.report_generator import IncidentReportGenerator
from sentinel_api.models.investigation import Investigation
from sentinel_api.repositories.investigation import InvestigationRepository

logger = structlog.get_logger("sentinel_api.services.investigation")


class InvestigationService:
    """Service layer coordinating coordinator workflow dispatches, consolidated reports, and persistence."""

    def __init__(self) -> None:
        self.repository = InvestigationRepository()
        self.coordinator = CoordinatorAgent()
        self.report_generator = IncidentReportGenerator()

    async def analyze_incident(
        self,
        db: AsyncSession,
        incident_id: str,
        severity: str,
        status: str,
        summary: str,
        logs: Optional[Any] = None,
        metrics: Optional[Any] = None,
        deployment_history: Optional[Any] = None,
        customer_reports: Optional[Any] = None,
    ) -> Investigation:
        """Dispatches execution across Coordinator and sub-agents, compiling and saving the report."""
        logger.info(
            f"Starting incident analysis workflow for incident_id={incident_id}"
        )

        signals = {
            "log_agent_output": logs,
            "metrics_agent_output": metrics,
            "deployment_agent_output": deployment_history,
            "review_agent_output": customer_reports,
        }
        signals = {k: v for k, v in signals.items() if v is not None}

        exec_context = ExecutionContext(
            request_id=f"req-{uuid.uuid4()}",
            correlation_id=f"corr-{uuid.uuid4()}",
            agent_id="coordinator-service",
        )
        incident_context = IncidentContext(
            incident_id=incident_id,
            severity=severity,
            status=status,
            summary=summary,
            signals=signals,
        )
        request = AgentRequest(
            execution_context=exec_context,
            incident_context=incident_context,
            inputs={},
        )

        config = ModelConfig(provider="openai", model_name="gpt-4")

        coordinator_result = await self.coordinator.execute(request, config)
        if not coordinator_result.success:
            logger.error(
                "Coordinator agent execution failed",
                error=coordinator_result.reasoning_summary,
            )
            raise RuntimeError(
                f"Incident coordination analysis failed:"
                f" {coordinator_result.reasoning_summary}"
            )

        agent_results = coordinator_result.output.get("agent_results", {})

        report_inputs = {}
        for agent_name, result in agent_results.items():
            res_dict = result if isinstance(result, dict) else result.model_dump()
            key_name = agent_name.lower().replace(" ", "_") + "_output"
            report_inputs[key_name] = res_dict.get("output")

        incident_ctx_dict = {
            "incident_id": incident_id,
            "severity": severity,
            "status": status,
            "summary": summary,
            "created_at": get_current_utc_timestamp(),
        }
        report = self.report_generator.generate_report(
            report_inputs, incident_ctx_dict
        )

        # Flat serializing of nested structures
        report_data = report.model_dump()
        raw_outputs = {}
        for k, v in report_inputs.items():
            if v:
                raw_outputs[k] = v

        investigation = await self.repository.create(
            db=db,
            incident_id=incident_id,
            severity=severity,
            status=status,
            summary=summary,
            agent_outputs=raw_outputs,
            incident_report=report_data,
        )
        return investigation

    async def get_investigation(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Optional[Investigation]:
        """Retrieves investigation details by record ID."""
        return await self.repository.get(db, id)

    async def delete_investigation(self, db: AsyncSession, id: uuid.UUID) -> bool:
        """Deletes investigation by record ID."""
        return await self.repository.delete(db, id)

    async def list_investigations(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Investigation]:
        """Queries historical investigation runs."""
        return await self.repository.list(
            db=db,
            skip=skip,
            limit=limit,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )


from sentinel_api.app.reporting.utils import get_current_utc_timestamp
