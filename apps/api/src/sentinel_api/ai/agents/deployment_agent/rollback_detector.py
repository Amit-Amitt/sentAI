from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.deployment_agent.schemas import DeploymentEvent

logger = structlog.get_logger(
    "sentinel_api.ai.agents.deployment_agent.rollback_detector"
)


class RollbackDetector:
    """Scans for rollbacks, deployment failures, and release strategies."""

    def detect_rollbacks(
        self, events: List[DeploymentEvent]
    ) -> List[Dict[str, Any]]:
        """Identifies failed or reverted rollouts and notes canary/bg usage."""
        logger.info("Detecting rollback or failure events")
        findings = []

        for ev in events:
            details = ev.details
            strategy = details.get("strategy") or details.get("deploy_style") or ""

            is_canary = "canary" in strategy.lower() or "canary" in str(details).lower()
            is_bg = (
                "blue-green" in strategy.lower()
                or "bg" in strategy.lower()
                or "blue-green" in str(details).lower()
            )
            is_partial = "partial" in strategy.lower() or "percent" in str(details).lower()

            style = "Standard"
            if is_canary:
                style = "Canary"
            elif is_bg:
                style = "Blue-Green"
            elif is_partial:
                style = "Partial"

            if ev.status in ["FAILED", "ROLLBACK"]:
                findings.append(
                    {
                        "deployment_id": ev.deployment_id,
                        "service": ev.service,
                        "version": ev.version,
                        "timestamp": ev.timestamp,
                        "issue_type": ev.status,
                        "style": style,
                        "description": (
                            f"Deployment issue on {ev.service}: Status is"
                            f" {ev.status} using {style} strategy."
                        ),
                    }
                )

        return findings
