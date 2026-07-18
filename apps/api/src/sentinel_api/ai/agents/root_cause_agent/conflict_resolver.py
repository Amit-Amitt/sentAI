from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.root_cause_agent.schemas import RootCauseHypothesis

logger = structlog.get_logger(
    "sentinel_api.ai.agents.root_cause_agent.conflict_resolver"
)


class ConflictResolver:
    """Detects discrepant data logs, adjusting hypothesis confidence values."""

    def resolve_conflicts(
        self,
        hypotheses: List[RootCauseHypothesis],
        normalized_evidence: List[Dict[str, Any]],
    ) -> List[RootCauseHypothesis]:
        """Lowers confidence if logs, metrics, or support reviews report contradictory states."""
        logger.info("Evaluating evidence conflict boundaries")

        logs = [e for e in normalized_evidence if e["agent"] == "LOG"]
        metrics = [e for e in normalized_evidence if e["agent"] == "METRICS"]
        reviews = [e for e in normalized_evidence if e["agent"] == "REVIEW"]

        has_review_payments_critical = any(
            "checkout" in e["description"].lower()
            or "pay" in e["description"].lower()
            for e in reviews
            if e["severity"] == "Critical"
        )
        has_metrics_no_anomalies = len(metrics) == 0
        has_logs_no_errors = len(logs) == 0

        for h in hypotheses:
            conflict_detected = False

            if (
                h.root_cause_type == "DATABASE_OVERLOAD"
                and has_metrics_no_anomalies
            ):
                logger.warning(
                    "Conflict detected: DB Overload hypothesis with no metrics"
                    " anomalies."
                )
                conflict_detected = True
                h.supporting_evidence.append(
                    "Warning: Metrics agent reports no database connection pool"
                    " anomalies."
                )

            if (
                h.root_cause_type == "AUTHENTICATION_FAILURE"
                and has_logs_no_errors
            ):
                logger.warning(
                    "Conflict detected: Auth failure hypothesis with no log"
                    " errors."
                )
                conflict_detected = True
                h.supporting_evidence.append(
                    "Warning: Log agent reports zero authentication error"
                    " patterns."
                )

            if conflict_detected:
                h.confidence = max(0.20, h.confidence - 0.15)

        return hypotheses
