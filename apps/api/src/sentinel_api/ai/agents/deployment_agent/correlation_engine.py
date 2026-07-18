from typing import Any, Dict, List, Optional
import structlog

from sentinel_api.ai.agents.deployment_agent.schemas import (
    DeploymentEvent,
    DeploymentFinding,
)
from sentinel_api.ai.agents.deployment_agent.utils import parse_timestamp

logger = structlog.get_logger("sentinel_api.ai.agents.deployment_agent.correlation_engine")


class CorrelationEngine:
    """Computes mathematical correlation ratings based on time delta and risk profile."""

    def correlate(
        self,
        events: List[DeploymentEvent],
        incident_time_str: Optional[str],
        risk_profiles: Dict[str, Dict[str, Any]],
    ) -> List[DeploymentFinding]:
        """Correlates deployments to the incident timeframe."""
        logger.info("Computing incident-deployment correlations")
        findings: List[DeploymentFinding] = []

        if not incident_time_str or not events:
            return findings

        incident_time = parse_timestamp(incident_time_str)

        for ev in events:
            ev_time = parse_timestamp(ev.timestamp)

            diff_sec = (incident_time - ev_time).total_seconds()
            diff_min = diff_sec / 60.0

            if diff_sec < 0:
                if ev.status == "ROLLBACK":
                    correlation_score = 0.3
                else:
                    correlation_score = 0.0
            else:
                if diff_min <= 15.0:
                    temporal_score = 1.0
                elif diff_min <= 60.0:
                    temporal_score = 0.8
                elif diff_min <= 120.0:
                    temporal_score = 0.5
                elif diff_min <= 240.0:
                    temporal_score = 0.2
                else:
                    temporal_score = 0.05

                profile = risk_profiles.get(ev.deployment_id) or {
                    "risk_score": 0.1,
                    "reasons": [],
                }
                risk_score = profile.get("risk_score", 0.1)

                correlation_score = temporal_score * (0.6 + 0.4 * risk_score)

            completeness = 0.8
            if ev.details.get("commits") or ev.details.get("keys_changed"):
                completeness += 0.2
            confidence = min(1.0, correlation_score * completeness)

            if correlation_score > 0.1:
                profile = risk_profiles.get(ev.deployment_id) or {"reasons": []}
                reasons = profile.get("reasons") or []
                reasons_str = (
                    f" (Flags: {', '.join(reasons)})" if reasons else ""
                )

                summary = (
                    f"Deployment of {ev.service} (Version: {ev.version})"
                    f" occurred {abs(diff_min):.1f} minutes before incident."
                    f" Correlation: {correlation_score:.2f}, Confidence:"
                    f" {confidence:.2f}.{reasons_str}"
                )

                findings.append(
                    DeploymentFinding(
                        deployment_id=ev.deployment_id,
                        version=ev.version,
                        timestamp=ev.timestamp,
                        affected_services=[ev.service],
                        change_type=ev.change_type,
                        correlation_score=round(correlation_score, 2),
                        confidence=round(confidence, 2),
                        summary=summary,
                    )
                )

        return sorted(findings, key=lambda x: x.correlation_score, reverse=True)
