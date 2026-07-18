from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.impact_analyzer"
)


class ImpactAnalyzer:
    """Analyzes recovery metrics, estimating resolution time and service footprint."""

    def analyze_impact(
        self,
        affected_services: List[str],
        actions: List[Any],
        incident_priority: str,
    ) -> Dict[str, Any]:
        """Estimates recovery times and customer impacts from actions list."""
        logger.info("Analyzing recovery impact details")

        est_recovery_min = 5
        action_types = [a.action_type for a in actions]

        if "ROLLBACK" in action_types:
            est_recovery_min = 15
        elif "SCALE" in action_types:
            est_recovery_min = 10

        customer_impact = "Low"
        if incident_priority in ["Critical", "High"]:
            customer_impact = "High"

        return {
            "estimated_recovery_time_minutes": est_recovery_min,
            "affected_services": affected_services,
            "business_impact_level": incident_priority,
            "customer_impact_level": customer_impact,
        }
