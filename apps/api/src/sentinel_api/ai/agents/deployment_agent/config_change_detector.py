from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.deployment_agent.schemas import DeploymentEvent

logger = structlog.get_logger(
    "sentinel_api.ai.agents.deployment_agent.config_change_detector"
)


class ConfigChangeDetector:
    """Analyzes configuration and secret deployments to flag risk levels."""

    def analyze_config_changes(
        self, config_events: List[DeploymentEvent]
    ) -> List[Dict[str, Any]]:
        """Scans CONFIG events to detect secret exposures or structural changes."""
        logger.info("Scanning CONFIG change details")
        findings = []

        for ev in config_events:
            details = ev.details
            keys = details.get("keys_changed") or details.get("keys") or []
            if isinstance(keys, str):
                keys = [keys]

            is_secret = details.get("is_secret") or any(
                "secret" in str(k).lower()
                or "password" in str(k).lower()
                or "token" in str(k).lower()
                for k in keys
            )

            findings.append(
                {
                    "deployment_id": ev.deployment_id,
                    "service": ev.service,
                    "version": ev.version,
                    "timestamp": ev.timestamp,
                    "keys_changed": keys,
                    "is_secret": bool(is_secret),
                    "risk_level": "High" if is_secret else "Medium",
                }
            )

        return findings
