from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.root_cause_agent.schemas import RootCauseHypothesis

logger = structlog.get_logger(
    "sentinel_api.ai.agents.root_cause_agent.confidence_engine"
)


class ConfidenceEngine:
    """Calculates final agent confidence using source and ranking factors."""

    def calculate_confidence(
        self,
        ranked_hypotheses: List[RootCauseHypothesis],
        normalized_evidence: List[Dict[str, Any]],
        signals: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculates overall, per-hypothesis, and source agent evidence quality."""
        logger.info("Evaluating reasoning confidence matrix")

        agent_confidences = []
        for agent_key in [
            "log_agent_output",
            "metrics_agent_output",
            "deployment_agent_output",
            "review_agent_output",
        ]:
            data = signals.get(agent_key) or signals.get(
                agent_key.replace("_output", "")
            )
            if data and isinstance(data, dict):
                agent_confidences.append(data.get("confidence", 0.8))

        evidence_quality = (
            sum(agent_confidences) / len(agent_confidences)
            if agent_confidences
            else 0.75
        )

        top_score = ranked_hypotheses[0].score if ranked_hypotheses else 0.5
        overall = (top_score * 0.7) + (evidence_quality * 0.3)

        return {
            "overall_confidence": round(min(0.98, max(0.10, overall)), 2),
            "evidence_quality_score": round(evidence_quality, 2),
            "top_hypothesis_score": round(top_score, 2),
        }
