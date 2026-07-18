import time
from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.recommendation_agent.action_generator import (
    ActionGenerator,
)
from sentinel_api.ai.agents.recommendation_agent.impact_analyzer import (
    ImpactAnalyzer,
)
from sentinel_api.ai.agents.recommendation_agent.playbook_selector import (
    PlaybookSelector,
)
from sentinel_api.ai.agents.recommendation_agent.priority_engine import (
    PriorityEngine,
)
from sentinel_api.ai.agents.recommendation_agent.risk_assessor import (
    RiskAssessor,
)
from sentinel_api.ai.agents.recommendation_agent.rollback_advisor import (
    RollbackAdvisor,
)
from sentinel_api.ai.agents.recommendation_agent.runbook_matcher import (
    RunbookMatcher,
)
from sentinel_api.ai.agents.recommendation_agent.schemas import (
    RecommendationAgentOutput,
    RecoveryMonitoringPlan,
)
from sentinel_api.ai.agents.recommendation_agent.summary_generator import (
    SummaryGenerator,
)
from sentinel_api.ai.agents.recommendation_agent.validation_checker import (
    ValidationChecker,
)
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import AgentRequest

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.recommendation_agent"
)


class RecommendationAgent(BaseAgent):
    """Processes final root cause analysis results to draft SRE mitigation recommendations."""

    def __init__(self) -> None:
        super().__init__(name="Recommendation Agent")
        self.action_generator = ActionGenerator()
        self.priority_engine = PriorityEngine()
        self.risk_assessor = RiskAssessor()
        self.impact_analyzer = ImpactAnalyzer()
        self.rollback_advisor = RollbackAdvisor()
        self.runbook_matcher = RunbookMatcher()
        self.playbook_selector = PlaybookSelector()
        self.validation_checker = ValidationChecker()
        self.summary_generator = SummaryGenerator()

    def validate(self, request: AgentRequest) -> None:
        """Validates that a root cause statement is present in request signals or inputs."""
        super().validate(request)

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        root_cause = (
            signals.get("root_cause")
            or signals.get("root_cause_agent_output", {}).get("root_cause")
            or inputs.get("root_cause")
            or inputs.get("root_cause_agent_output", {}).get("root_cause")
        )

        if not root_cause:
            raise AgentException(
                "Recommendation Agent requires a diagnosed root cause input."
            )

    async def _run(
        self, request: AgentRequest, config: ModelConfig
    ) -> Dict[str, Any]:
        """Runs the recommendation planning engine."""
        start_time = time.perf_counter()

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        # 1. Resolve inputs
        rc_output = (
            signals.get("root_cause_agent_output")
            or inputs.get("root_cause_agent_output")
            or {}
        )
        root_cause = (
            signals.get("root_cause")
            or rc_output.get("root_cause")
            or inputs.get("root_cause")
            or "Unknown incident issue"
        )
        if isinstance(root_cause, dict):
            root_cause = root_cause.get("root_cause") or root_cause.get("summary") or "Unknown incident issue"
        rc_confidence_val = (
            signals.get("confidence")
            or rc_output.get("confidence")
            or (inputs.get("root_cause").get("confidence") if isinstance(inputs.get("root_cause"), dict) else None)
            or inputs.get("confidence")
            or 0.85
        )
        rc_confidence = float(rc_confidence_val)

        affected_services = (
            signals.get("affected_services")
            or rc_output.get("evidence_sources")
            or ["payment-service"]
        )
        # Fallback to string if affected services is a string
        if isinstance(affected_services, str):
            affected_services = [affected_services]

        severity = request.incident_context.severity or "SEV2"

        # 2. Action Generation
        actions = self.action_generator.generate_actions(
            root_cause, affected_services
        )

        # 3. Prioritization
        priority_details = self.priority_engine.prioritize(actions, severity)
        prioritized_actions = priority_details["prioritized_actions"]
        incident_priority = priority_details["incident_priority"]
        execution_order = priority_details["execution_order"]

        # 4. Risk Assessment
        risk = self.risk_assessor.assess_risk(prioritized_actions, rc_confidence)

        # 5. Impact Analysis
        impact = self.impact_analyzer.analyze_impact(
            affected_services, prioritized_actions, incident_priority
        )

        # 6. Rollback Advisor
        rollback = self.rollback_advisor.get_rollback_advice(
            root_cause, affected_services
        )

        # 7. Playbook & Runbook Mapping
        runbook = self.runbook_matcher.match_runbook(root_cause)
        rc_type = "BAD_DEPLOYMENT" if "DEPLOY" in root_cause.upper() else "DATABASE_OVERLOAD"
        playbook = self.playbook_selector.select_playbook(rc_type)

        # 8. Validation Checking
        checks = self.validation_checker.generate_validation_checks(
            rc_type, affected_services
        )

        # 9. Monitoring Plan
        mon_metrics = (
            ["http_requests_total", "http_request_duration_seconds"]
            if rc_type == "BAD_DEPLOYMENT"
            else ["db_connection_failures_count", "db_active_connections"]
        )
        monitoring_plan = RecoveryMonitoringPlan(
            metrics_to_watch=mon_metrics,
            duration_minutes=impact["estimated_recovery_time_minutes"],
            success_criteria=(
                "API Gateway error rate is under 0.1% and response latencies"
                " are normalized."
            ),
            rollback_verification_steps=rollback["verification_steps"],
        )

        # 10. Summaries
        summaries = self.summary_generator.generate_summaries(
            root_cause, incident_priority, affected_services, prioritized_actions
        )

        duration_ms = (time.perf_counter() - start_time) * 1000

        output = RecommendationAgentOutput(
            agent_name=self.name,
            execution_time_ms=duration_ms,
            status="SUCCESS",
            confidence=risk.confidence,
            incident_priority=incident_priority,
            recommended_actions=prioritized_actions,
            execution_order=execution_order,
            risk_assessment=risk,
            validation_checklist=checks,
            recovery_monitoring_plan=monitoring_plan,
            executive_summary=summaries["executive_summary"],
            technical_summary=summaries["technical_summary"],
            business_summary=summaries["business_summary"],
            metadata={
                "affected_services": affected_services,
                "recovery_impact_analysis": impact,
                "rollback_advisory": rollback,
                "runbook_mapping": runbook,
                "playbook_mapping": playbook,
            },
        )

        result_dict = output.model_dump()
        result_dict["reasoning_summary"] = summaries["executive_summary"]
        return result_dict
