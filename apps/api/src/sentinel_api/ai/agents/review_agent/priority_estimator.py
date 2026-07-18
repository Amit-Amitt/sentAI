from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.review_agent.schemas import ReviewItem

logger = structlog.get_logger(
    "sentinel_api.ai.agents.review_agent.priority_estimator"
)


class PriorityEstimator:
    """Estimates user, business, and urgency impact profiles for ticket clusters."""

    def estimate_priority(
        self, cluster: List[ReviewItem], sentiments: List[str]
    ) -> Dict[str, Any]:
        """Runs rule checks to compute severity levels."""
        logger.info("Computing severity prioritization scores")

        has_critical = any(s == "Critical" for s in sentiments)
        negative_count = sum(1 for s in sentiments if s in ["Negative", "Critical"])

        neg_ratio = negative_count / len(cluster) if cluster else 0

        if has_critical:
            user_impact = "Critical"
            urgency = "Immediate"
            severity = "Critical"
        elif neg_ratio >= 0.7:
            user_impact = "High"
            urgency = "High"
            severity = "High"
        elif neg_ratio >= 0.3:
            user_impact = "Medium"
            urgency = "Medium"
            severity = "Medium"
        else:
            user_impact = "Low"
            urgency = "Low"
            severity = "Low"

        affects_core = any(
            any(
                w in item.content.lower()
                for w in ["pay", "checkout", "billing", "cart", "charge", "card"]
            )
            for item in cluster
        )

        if affects_core:
            business_impact = "High"
            if severity == "High":
                severity = "Critical"
        else:
            business_impact = "Medium" if severity in ["High", "Critical"] else "Low"

        return {
            "severity": severity,
            "user_impact": user_impact,
            "business_impact": business_impact,
            "urgency": urgency,
            "frequency_score": len(cluster),
        }
