from typing import List
import structlog

from sentinel_api.ai.agents.recommendation_agent.schemas import (
    RecommendedAction,
    RiskAssessment,
)

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.risk_assessor"
)


class RiskAssessor:
    """Evaluates the risk of executing the recommended recovery actions."""

    def assess_risk(
        self, actions: List[RecommendedAction], root_cause_confidence: float
    ) -> RiskAssessment:
        """Evaluates overall plan safety using individual step risk matrices."""
        logger.info("Assessing execution risk levels")

        risk_map = {"Low": 0.2, "Medium": 0.5, "High": 0.8}

        highest_action_risk = "Low"
        side_effects = []

        for act in actions:
            if risk_map.get(act.risk_level, 0.2) > risk_map.get(
                highest_action_risk, 0.2
            ):
                highest_action_risk = act.risk_level
            side_effects.extend(act.side_effects)

        base_risk = risk_map.get(highest_action_risk, 0.2)
        risk_score = base_risk * (1.2 - root_cause_confidence)
        risk_score = round(min(0.95, max(0.05, risk_score)), 2)

        rollback_difficulty = "Low"
        if any(act.action_type in ["ROLLBACK", "SCALE"] for act in actions):
            rollback_difficulty = "Medium"

        business_impact = "Low"
        if highest_action_risk == "High":
            business_impact = "Medium"

        return RiskAssessment(
            risk_score=risk_score,
            potential_side_effects=list(set(side_effects)),
            rollback_difficulty=rollback_difficulty,
            business_impact=business_impact,
            confidence=round(root_cause_confidence, 2),
        )
