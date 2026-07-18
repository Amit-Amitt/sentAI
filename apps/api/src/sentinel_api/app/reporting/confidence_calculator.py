from typing import Any, Dict
import structlog

from sentinel_api.app.reporting.schemas import ConfidenceSummarySection

logger = structlog.get_logger("sentinel_api.app.reporting.confidence_calculator")


class ConfidenceCalculator:
    """Calculates overall diagnostic pipeline confidence and telemetry source metrics."""

    def calculate(
        self,
        coordinator_output: Dict[str, Any],
        log_output: Dict[str, Any],
        metrics_output: Dict[str, Any],
        deployment_output: Dict[str, Any],
        review_output: Dict[str, Any],
        root_cause_output: Dict[str, Any],
        recommendation_output: Dict[str, Any],
    ) -> ConfidenceSummarySection:
        """Evaluates pipeline coverage score and evidence source quality averages."""
        logger.info("Computing report confidence summaries")

        agents = {
            "Coordinator Agent": coordinator_output,
            "Log Agent": log_output,
            "Metrics Agent": metrics_output,
            "Deployment Agent": deployment_output,
            "Review Agent": review_output,
            "Root Cause Agent": root_cause_output,
            "Recommendation Agent": recommendation_output,
        }

        active_agents = [
            name
            for name, out in agents.items()
            if out and out.get("success") is not False
        ]
        coverage_score = round(len(active_agents) / len(agents), 2)

        conf_summary = {}
        for name, out in agents.items():
            if out:
                conf_val = out.get("confidence") or 0.85
                conf_summary[name] = float(conf_val)

        overall_confidence = (
            float(root_cause_output.get("confidence") or 0.85)
            if root_cause_output
            else 0.85
        )

        evidence_agents = [
            "Log Agent",
            "Metrics Agent",
            "Deployment Agent",
            "Review Agent",
        ]
        evidence_confs = [
            conf_summary[name] for name in evidence_agents if name in conf_summary
        ]
        evidence_quality = (
            round(sum(evidence_confs) / len(evidence_confs), 2)
            if evidence_confs
            else 0.85
        )

        return ConfidenceSummarySection(
            overall_confidence=overall_confidence,
            evidence_quality=evidence_quality,
            coverage_score=coverage_score,
            agent_confidence_summary=conf_summary,
        )
