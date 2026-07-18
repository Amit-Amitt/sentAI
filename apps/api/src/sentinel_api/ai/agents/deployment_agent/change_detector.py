from typing import Dict, List
import structlog

from sentinel_api.ai.agents.deployment_agent.schemas import DeploymentEvent

logger = structlog.get_logger("sentinel_api.ai.agents.deployment_agent.change_detector")


class ChangeDetector:
    """Classifies incoming deployment events by modification category."""

    def detect_changes(
        self, events: List[DeploymentEvent]
    ) -> Dict[str, List[DeploymentEvent]]:
        """Splits deployment list into APP, CONFIG, FLAG, INFRA, DB lists."""
        logger.info("Classifying system changes")
        classified: Dict[str, List[DeploymentEvent]] = {
            "APP": [],
            "CONFIG": [],
            "FLAG": [],
            "INFRA": [],
            "DB": [],
        }

        for ev in events:
            if ev.change_type in classified:
                classified[ev.change_type].append(ev)
            else:
                classified["APP"].append(ev)

        return classified
