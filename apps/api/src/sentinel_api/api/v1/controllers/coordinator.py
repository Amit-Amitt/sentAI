from fastapi import HTTPException

from sentinel_api.ai.agents.coordinator import CoordinatorAgent
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)
from sentinel_api.api.v1.validators.schemas import CoordinatorRunRequest


class CoordinatorController:
    """Controller handling manual Coordinator execution invocations."""

    def __init__(self) -> None:
        self.coordinator = CoordinatorAgent()

    async def run(self, payload: CoordinatorRunRequest) -> dict:
        """Executes the coordinator pipeline and returns the execution states."""
        try:
            exec_ctx = ExecutionContext(
                request_id=payload.execution_context.get("request_id")
                or "manual-req",
                correlation_id=payload.execution_context.get("correlation_id")
                or "manual-corr",
                agent_id="coordinator-manual",
            )
            incident_ctx = IncidentContext(
                incident_id=payload.incident_context.get("incident_id")
                or "INC-MANUAL",
                severity=payload.incident_context.get("severity") or "SEV2",
                status=payload.incident_context.get("status") or "active",
                summary=payload.incident_context.get("summary")
                or "Manual test run",
                signals=payload.incident_context.get("signals") or {},
            )
            request = AgentRequest(
                execution_context=exec_ctx,
                incident_context=incident_ctx,
                inputs=payload.inputs or {},
            )
            config = ModelConfig(provider="openai", model_name="gpt-4")
            result = await self.coordinator.execute(request, config)
            if not result.success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Coordinator run failed: {result.reasoning_summary}",
                )
            return result.output
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
