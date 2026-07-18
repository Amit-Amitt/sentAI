from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.root_cause_agent.utils import parse_timestamp
from sentinel_api.app.reporting.schemas import TimelineEvent
from sentinel_api.app.reporting.utils import get_current_utc_timestamp

logger = structlog.get_logger("sentinel_api.app.reporting.timeline_builder")


class TimelineBuilder:
    """Consolidates timeline events across all agents into a single sorted chronological list."""

    def build_timeline(
        self,
        coordinator_output: Dict[str, Any],
        log_output: Dict[str, Any],
        metrics_output: Dict[str, Any],
        deployment_output: Dict[str, Any],
        review_output: Dict[str, Any],
        root_cause_output: Dict[str, Any],
        recommendation_output: Dict[str, Any],
    ) -> List[TimelineEvent]:
        """Collects, standardizes, and sorts all timeline markers from agent outputs."""
        logger.info("Assembling incident event timeline")
        events: List[TimelineEvent] = []

        # 1. Incident Detected
        if coordinator_output:
            created_at = (
                coordinator_output.get("metadata", {}).get(
                    "execution_start_time"
                )
                or ""
            )
            if created_at:
                events.append(
                    TimelineEvent(
                        timestamp=created_at,
                        event_type="INCIDENT_START",
                        description=(
                            "Incident response started, Coordinator Agent"
                            " initialized."
                        ),
                        details={},
                    )
                )

        # 2. Log events
        if log_output and isinstance(log_output, dict):
            findings = log_output.get("findings") or []
            for f in findings:
                if f.get("timestamp"):
                    events.append(
                        TimelineEvent(
                            timestamp=f["timestamp"],
                            event_type="LOG",
                            description=(
                                f"Log Pattern Error: {f.get('pattern_name')}"
                            ),
                            details=f,
                        )
                    )

        # 3. Metric anomalies
        if metrics_output and isinstance(metrics_output, dict):
            findings = (
                metrics_output.get("anomaly_clusters")
                or metrics_output.get("findings")
                or []
            )
            for f in findings:
                if f.get("timestamp"):
                    events.append(
                        TimelineEvent(
                            timestamp=f["timestamp"],
                            event_type="METRICS",
                            description=(
                                f"Metric Anomaly: {f.get('metric_name')}"
                            ),
                            details=f,
                        )
                    )

        # 4. Deployments
        if deployment_output and isinstance(deployment_output, dict):
            findings = (
                deployment_output.get("correlated_events")
                or deployment_output.get("findings")
                or []
            )
            for f in findings:
                if f.get("timestamp"):
                    events.append(
                        TimelineEvent(
                            timestamp=f["timestamp"],
                            event_type="DEPLOYMENT",
                            description=(
                                f"Deployment Change: {f.get('description')}"
                            ),
                            details=f,
                        )
                    )

        # 5. Customer reports
        if review_output and isinstance(review_output, dict):
            first_rep = (
                review_output.get("metadata", {})
                .get("timeline_stats", {})
                .get("first_report")
            )
            if first_rep:
                events.append(
                    TimelineEvent(
                        timestamp=first_rep,
                        event_type="REVIEW",
                        description="First customer feedback ticket report logged.",
                        details={},
                    )
                )

        # 6. Root Cause Identified
        if root_cause_output and isinstance(root_cause_output, dict):
            events.append(
                TimelineEvent(
                    timestamp=(
                        root_cause_output.get("metadata", {}).get(
                            "incident_timestamp"
                        )
                        or get_current_utc_timestamp()
                    ),
                    event_type="ROOT_CAUSE",
                    description=(
                        f"Root cause identified:"
                        f" {root_cause_output.get('root_cause')}"
                    ),
                    details={"confidence": root_cause_output.get("confidence")},
                )
            )

        # 7. Recommendations generated
        if recommendation_output and isinstance(recommendation_output, dict):
            events.append(
                TimelineEvent(
                    timestamp=get_current_utc_timestamp(),
                    event_type="RECOMMENDATIONS",
                    description=(
                        f"Response recommendation playbook generated with"
                        f" {len(recommendation_output.get('recommended_actions', []))} actions."
                    ),
                    details={},
                )
            )

        # Remove duplicate timestamps or sort safely
        events.sort(
            key=lambda x: parse_timestamp(x.timestamp)
            if x.timestamp
            else parse_timestamp(get_current_utc_timestamp())
        )
        return events
