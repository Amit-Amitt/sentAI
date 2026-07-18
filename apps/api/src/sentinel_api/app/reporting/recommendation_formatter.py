from typing import Any, Dict
import structlog

from sentinel_api.app.reporting.schemas import RecommendationSection

logger = structlog.get_logger("sentinel_api.app.reporting.recommendation_formatter")


class RecommendationFormatter:
    """Formats recommendations into categories based on priority and sequence."""

    def format_recommendations(
        self, recommendation_output: Dict[str, Any]
    ) -> RecommendationSection:
        """Splits recommendations by priority weights and SRE types."""
        logger.info("Formatting incident recovery recommendations")

        actions = recommendation_output.get("recommended_actions") or []

        immediate = []
        short_term = []
        long_term = []

        for act in actions:
            act_dict = act if isinstance(act, dict) else act.model_dump()
            prio = act_dict.get("priority", "Medium")
            act_type = act_dict.get("action_type", "MONITOR")

            if prio in ["Critical", "High"] and act_type in [
                "ROLLBACK",
                "SCALE",
                "RESTART",
                "VERIFY_CREDENTIALS",
            ]:
                immediate.append(act_dict)
            elif prio in ["High", "Medium"]:
                short_term.append(act_dict)
            else:
                long_term.append(act_dict)

        if not immediate and actions:
            first_act = actions[0]
            first_dict = (
                first_act if isinstance(first_act, dict) else first_act.model_dump()
            )
            immediate.append(first_dict)

        risk_data = recommendation_output.get("risk_assessment") or {}
        risk_level = "Low"
        if isinstance(risk_data, dict):
            risk_score = risk_data.get("risk_score", 0.0)
            if risk_score > 0.6:
                risk_level = "High"
            elif risk_score > 0.3:
                risk_level = "Medium"
        else:
            risk_score = getattr(risk_data, "risk_score", 0.0)
            if risk_score > 0.6:
                risk_level = "High"
            elif risk_score > 0.3:
                risk_level = "Medium"

        return RecommendationSection(
            immediate_actions=immediate,
            short_term_actions=short_term,
            long_term_improvements=long_term,
            priority=recommendation_output.get("incident_priority") or "Medium",
            risk=risk_level,
        )
