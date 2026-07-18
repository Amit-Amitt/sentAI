import structlog

from sentinel_api.ai.agents.coordinator.models import (
    AgentStatus,
    ExecutionPlan,
    ExecutionPlanItem,
)
from sentinel_api.ai.schemas.models import IncidentContext

logger = structlog.get_logger("sentinel_api.ai.agents.coordinator.planner")


class IncidentPlanner:
    """Constructs dynamic execution plans tailored to specific incident contexts."""

    def create_plan(self, incident: IncidentContext) -> ExecutionPlan:
        """Determines agent inclusion, priorities, timeouts, and dependencies

        by analyzing incident severity and telemetry signals.
        """
        logger.info(
            "Generating incident investigation plan",
            incident_id=incident.incident_id,
            severity=incident.severity,
        )

        items = {}

        # 1. Log Agent (Core agent)
        items["Log Agent"] = ExecutionPlanItem(
            agent_name="Log Agent",
            priority=10,
            dependencies=[],
            status=AgentStatus.PENDING,
            timeout=15.0,
        )

        # 2. Metrics Agent
        # Check signals if metrics collection should be skipped
        metrics_status = AgentStatus.PENDING
        if incident.signals.get("skip_metrics") is True:
            metrics_status = AgentStatus.SKIPPED
            logger.info("Metrics Agent marked as SKIPPED based on signals.")

        items["Metrics Agent"] = ExecutionPlanItem(
            agent_name="Metrics Agent",
            priority=20,
            dependencies=[],
            status=metrics_status,
            timeout=15.0,
        )

        # 3. Deployment Agent
        # Skipped for SEV3/SEV4 incidents unless explicit review is requested
        deployment_status = AgentStatus.PENDING
        if incident.severity in ["SEV3", "SEV4"] and not incident.signals.get(
            "force_deployment_check"
        ):
            deployment_status = AgentStatus.SKIPPED
            logger.info(
                "Deployment Agent marked as SKIPPED due to low severity context."
            )

        items["Deployment Agent"] = ExecutionPlanItem(
            agent_name="Deployment Agent",
            priority=30,
            dependencies=[],
            status=deployment_status,
            timeout=20.0,
        )

        # 4. Review Agent
        # Review Agent relies on Deployment Agent outputs, so skip if Deployment Agent is skipped
        review_status = AgentStatus.PENDING
        if (
            deployment_status == AgentStatus.SKIPPED
            or incident.signals.get("skip_review") is True
        ):
            review_status = AgentStatus.SKIPPED
            logger.info("Review Agent marked as SKIPPED.")

        items["Review Agent"] = ExecutionPlanItem(
            agent_name="Review Agent",
            priority=40,
            dependencies=(
                ["Deployment Agent"]
                if deployment_status != AgentStatus.SKIPPED
                else []
            ),
            status=review_status,
            timeout=25.0,
        )

        # 5. Root Cause Agent
        # Relies on Log Agent and (if present) Metrics Agent
        root_cause_deps = ["Log Agent"]
        if metrics_status != AgentStatus.SKIPPED:
            root_cause_deps.append("Metrics Agent")

        items["Root Cause Agent"] = ExecutionPlanItem(
            agent_name="Root Cause Agent",
            priority=50,
            dependencies=root_cause_deps,
            status=AgentStatus.PENDING,
            timeout=30.0,
        )

        # 6. Recommendation Agent
        # Relies on Root Cause Agent findings
        items["Recommendation Agent"] = ExecutionPlanItem(
            agent_name="Recommendation Agent",
            priority=60,
            dependencies=["Root Cause Agent"],
            status=AgentStatus.PENDING,
            timeout=30.0,
        )

        return ExecutionPlan(items=items)
