from typing import List, Optional
import structlog

from sentinel_api.ai.agents.deployment_agent.schemas import (
    DeploymentEvent,
    DeploymentTimelineEvent,
)
from sentinel_api.ai.agents.deployment_agent.utils import parse_timestamp

logger = structlog.get_logger("sentinel_api.ai.agents.deployment_agent.timeline_builder")


class TimelineBuilder:
    """Builds a sorted chronological deployment history, highlighting proximity to incidents."""

    def build_timeline(
        self,
        events: List[DeploymentEvent],
        incident_time_str: Optional[str] = None,
    ) -> List[DeploymentTimelineEvent]:
        """Orders events by time and attaches notes on temporal relation to the incident."""
        logger.info("Building sorted deployment timeline")

        sorted_events = sorted(
            events, key=lambda x: parse_timestamp(x.timestamp)
        )
        timeline: List[DeploymentTimelineEvent] = []

        incident_time = (
            parse_timestamp(incident_time_str) if incident_time_str else None
        )

        for ev in sorted_events:
            ev_time = parse_timestamp(ev.timestamp)
            desc = (
                f"Deployed {ev.change_type} change for {ev.service} (Version:"
                f" {ev.version}) with status: {ev.status}"
            )

            timing_note = ""
            if incident_time:
                diff_sec = (ev_time - incident_time).total_seconds()
                diff_min = diff_sec / 60.0

                if diff_sec < 0:
                    abs_min = abs(diff_min)
                    if abs_min <= 15:
                        timing_note = (
                            f" [CRITICAL TIMING: {abs_min:.1f} mins before"
                            " incident]"
                        )
                    elif abs_min <= 60:
                        timing_note = (
                            f" [HIGH TIMING PROXIMITY: {abs_min:.1f} mins"
                            " before incident]"
                        )
                    else:
                        timing_note = f" [{abs_min:.1f} mins before incident]"
                else:
                    timing_note = (
                        f" [{diff_min:.1f} mins after incident - post-incident"
                        " action]"
                    )

            desc += timing_note

            timeline.append(
                DeploymentTimelineEvent(
                    timestamp=ev.timestamp,
                    event_type=f"{ev.change_type}_{ev.status}",
                    description=desc,
                    service=ev.service,
                    details=ev.details,
                )
            )

        return timeline
