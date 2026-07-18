from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.recommendation_agent.schemas import (
    RecommendedAction,
)

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.priority_engine"
)


class PriorityEngine:
    """Calculates overall mitigation urgency and resets execution sequences."""

    def prioritize(
        self, actions: List[RecommendedAction], incident_severity: str
    ) -> Dict[str, Any]:
        """Calculates prioritized order based on incident severity maps."""
        logger.info(f"Prioritizing actions under severity: {incident_severity}")

        priority_map = {
            "SEV1": "Critical",
            "SEV2": "High",
            "SEV3": "Medium",
            "SEV4": "Low",
        }
        overall_priority = priority_map.get(incident_severity, "Medium")

        def get_priority_weight(a: RecommendedAction) -> int:
            weight_map = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
            return weight_map.get(a.priority, 3)

        sorted_actions = sorted(
            actions, key=lambda x: (get_priority_weight(x), x.execution_order)
        )

        for idx, act in enumerate(sorted_actions):
            act.execution_order = idx + 1

        return {
            "incident_priority": overall_priority,
            "prioritized_actions": sorted_actions,
            "execution_order": [act.id for act in sorted_actions],
        }
