from typing import Any, Dict
import structlog

logger = structlog.get_logger("sentinel_api.app.reporting.risk_summary")


class RiskSummaryBuilder:
    """Summarizes recommended action risk factors."""

    def build_risk_summary(
        self, recommendation_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Formats and wraps risk assessments from recommendation models."""
        logger.info("Extracting operational recovery risks")
        risk_data = recommendation_output.get("risk_assessment") or {}

        return {
            "risk_score": risk_data.get("risk_score") or 0.0,
            "potential_side_effects": risk_data.get("potential_side_effects")
            or [],
            "rollback_difficulty": risk_data.get("rollback_difficulty") or "Low",
            "business_impact": risk_data.get("business_impact") or "Low",
            "confidence": risk_data.get("confidence") or 0.0,
        }
