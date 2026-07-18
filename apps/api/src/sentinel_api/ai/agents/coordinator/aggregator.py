from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.coordinator.models import FinalExecutionState
from sentinel_api.ai.agents.coordinator.state_manager import StateManager
from sentinel_api.ai.schemas.models import AgentResult, IncidentContext

logger = structlog.get_logger("sentinel_api.ai.agents.coordinator.aggregator")


class ResultAggregator:
    """Aggregates outputs, confidences, metadata, and error reports from all executed agents."""

    def aggregate(
        self,
        incident: IncidentContext,
        agent_results: Dict[str, AgentResult],
        state_manager: StateManager,
        total_duration_ms: float,
    ) -> FinalExecutionState:
        """Parses individual agent execution reports into a consolidated FinalExecutionState."""
        logger.info("Aggregating agent results into final execution state")

        # 1. Incident Summary
        incident_summary = (
            f"Incident {incident.incident_id} [{incident.severity}] - {incident.summary}"
        )

        # 2. Execution Summary
        completed = state_manager.get_completed_agents()
        failed = state_manager.get_failed_agents()
        skipped = state_manager.get_skipped_agents()

        execution_summary = (
            f"Coordinator completed execution in {total_duration_ms:.2f} ms. "
            f"Completed Agents: {len(completed)}, Failed: {len(failed)}, Skipped: {len(skipped)}."
        )

        # 3. Overall Confidence calculation
        success_confidences = [
            res.confidence for res in agent_results.values() if res.success
        ]
        overall_confidence = 0.8  # default baseline
        if success_confidences:
            overall_confidence = sum(success_confidences) / len(
                success_confidences
            )

        # 4. Error extraction
        errors: List[Dict[str, Any]] = []
        for agent_name, res in agent_results.items():
            if not res.success:
                errors.append(
                    {
                        "agent": agent_name,
                        "error_summary": res.reasoning_summary,
                        "details": res.output,
                    }
                )

        # Collect failed retry events from timeline
        for event in state_manager.timeline:
            if event.get("event") == "execution_failed":
                errors.append(
                    {
                        "agent": event.get("agent_name"),
                        "error": event.get("error"),
                        "attempt": event.get("attempt"),
                    }
                )

        # 5. Recommendation extraction
        recommendations: List[str] = []
        for res in agent_results.values():
            if (
                res.success
                and isinstance(res.output, dict)
                and "recommendations" in res.output
            ):
                recommendations.extend(res.output["recommendations"])

        if not recommendations:
            recommendations.append(
                "Review server logs and metric signals to identify root cause."
            )

        return FinalExecutionState(
            incident_summary=incident_summary,
            execution_summary=execution_summary,
            agent_results=agent_results,
            overall_confidence=overall_confidence,
            errors=errors,
            recommendations=recommendations,
        )
