from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.deployment_agent.schemas import DeploymentEvent

logger = structlog.get_logger(
    "sentinel_api.ai.agents.deployment_agent.feature_flag_analyzer"
)


class FeatureFlagAnalyzer:
    """Evaluates risks of feature flag toggling and rollout ramps."""

    def analyze_flags(
        self, flag_events: List[DeploymentEvent]
    ) -> List[Dict[str, Any]]:
        """Scans FLAG events to determine change impacts and risk values."""
        logger.info("Evaluating feature flag configurations")
        findings = []

        for ev in flag_events:
            details = ev.details
            flag_name = (
                details.get("flag_name") or details.get("flag") or "unknown_flag"
            )
            old_val = details.get("old_value")
            new_val = details.get("new_value")

            old_pct = details.get("old_percentage") if details.get("old_percentage") is not None else details.get("old_pct")
            new_pct = details.get("new_percentage") if details.get("new_percentage") is not None else details.get("new_pct")

            risk = "Low"
            desc = f"Feature flag '{flag_name}' modified"

            if new_pct is not None and old_pct is not None:
                try:
                    op = float(old_pct)
                    np = float(new_pct)
                    if np > op:
                        desc = (
                            f"Feature flag '{flag_name}' rollout increased from"
                            f" {op}% to {np}%"
                        )
                        if np - op >= 50.0 or np == 100.0:
                            risk = "High"
                        else:
                            risk = "Medium"
                except (ValueError, TypeError):
                    pass
            elif str(new_val).lower() in ["true", "on", "enabled"] and str(
                old_val
            ).lower() not in ["true", "on", "enabled"]:
                desc = f"Feature flag '{flag_name}' toggled ON"
                risk = "High"
            elif str(new_val).lower() in ["false", "off", "disabled"]:
                desc = f"Feature flag '{flag_name}' toggled OFF"
                risk = "Low"

            findings.append(
                {
                    "deployment_id": ev.deployment_id,
                    "service": ev.service,
                    "flag_name": flag_name,
                    "old_value": old_val,
                    "new_value": new_val,
                    "description": desc,
                    "risk_level": risk,
                }
            )

        return findings
