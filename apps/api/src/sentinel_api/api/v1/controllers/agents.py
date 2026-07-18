from fastapi import HTTPException

from sentinel_api.ai.agents.deployment_agent.deployment_agent import (
    DeploymentAgent,
)
from sentinel_api.ai.agents.log_agent.log_agent import LogAgent
from sentinel_api.ai.agents.metrics_agent.metrics_agent import MetricsAgent
from sentinel_api.ai.agents.recommendation_agent.recommendation_agent import (
    RecommendationAgent,
)
from sentinel_api.ai.agents.review_agent.review_agent import ReviewAgent
from sentinel_api.ai.agents.root_cause_agent.root_cause_agent import RootCauseAgent
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)
from sentinel_api.api.v1.validators.schemas import AgentRunRequest

AGENT_MAP = {
    "log": LogAgent,
    "metrics": MetricsAgent,
    "deployment": DeploymentAgent,
    "review": ReviewAgent,
    "root-cause": RootCauseAgent,
    "recommendation": RecommendationAgent,
}


class AgentsController:
    """Controller handling individual agent standalone execution requests."""

    async def run_agent(self, agent_type: str, payload: AgentRunRequest) -> dict:
        """Instantiates and executes the targeted agent with request payloads."""
        agent_cls = AGENT_MAP.get(agent_type.lower())
        if not agent_cls:
            raise HTTPException(
                status_code=404, detail=f"Agent type not found: {agent_type}"
            )

        try:
            agent_inst = agent_cls()
            exec_ctx = ExecutionContext(
                request_id=payload.execution_context.get("request_id")
                or "agent-req",
                correlation_id=payload.execution_context.get("correlation_id")
                or "agent-corr",
                agent_id=f"agent-{agent_type.lower()}",
            )
            incident_ctx = IncidentContext(
                incident_id=payload.incident_context.get("incident_id")
                or "INC-AGENT",
                severity=payload.incident_context.get("severity") or "SEV2",
                status=payload.incident_context.get("status") or "active",
                summary=payload.incident_context.get("summary")
                or "Single agent execution",
                signals=payload.incident_context.get("signals") or {},
            )
            request = AgentRequest(
                execution_context=exec_ctx,
                incident_context=incident_ctx,
                inputs=payload.inputs or {},
            )
            config = ModelConfig(provider="openai", model_name="gpt-4")
            result = await agent_inst.execute(request, config)
            if not result.success:
                from sentinel_api.ai.exceptions import AgentException
                raise AgentException(result.reasoning_summary)
            res_dict = (
                result if isinstance(result, dict) else result.model_dump()
            )
            return res_dict
        except Exception as e:
            from sentinel_api.ai.exceptions import AIPlatformException
            if isinstance(e, AIPlatformException):
                raise e
            raise HTTPException(status_code=400, detail=str(e))
