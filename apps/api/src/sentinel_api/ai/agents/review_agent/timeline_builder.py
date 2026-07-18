from typing import Any, Dict, List, Tuple
import structlog

from sentinel_api.ai.agents.review_agent.schemas import DetectedTrend, ReviewItem
from sentinel_api.ai.agents.review_agent.utils import parse_timestamp

logger = structlog.get_logger("sentinel_api.ai.agents.review_agent.timeline_builder")


class TimelineBuilder:
    """Builds report timelines, detects complaint spikes and growing volumes."""

    def analyze_timeline(
        self, items: List[ReviewItem]
    ) -> Tuple[Dict[str, Any], List[DetectedTrend]]:
        """Calculates temporal stats and trends from feedback timestamps."""
        logger.info("Analyzing ticket history and timing landmarks")

        if not items:
            return {
                "first_report": "",
                "latest_report": "",
                "peak_time": "",
                "frequency_per_hour": 0.0,
            }, []

        sorted_items = sorted(items, key=lambda x: parse_timestamp(x.timestamp))
        first_time = parse_timestamp(sorted_items[0].timestamp)
        latest_time = parse_timestamp(sorted_items[-1].timestamp)

        duration_sec = (latest_time - first_time).total_seconds()
        duration_hours = max(1.0, duration_sec / 3600.0)
        freq = len(items) / duration_hours

        hour_buckets: Dict[str, int] = {}
        for item in items:
            dt = parse_timestamp(item.timestamp)
            hour_str = dt.strftime("%Y-%m-%d %H:00")
            hour_buckets[hour_str] = hour_buckets.get(hour_str, 0) + 1

        peak_hour = max(hour_buckets, key=hour_buckets.get) if hour_buckets else ""
        peak_count = hour_buckets[peak_hour] if peak_hour else 0

        stats = {
            "first_report": sorted_items[0].timestamp,
            "latest_report": sorted_items[-1].timestamp,
            "peak_time": peak_hour,
            "peak_count": peak_count,
            "frequency_per_hour": round(freq, 2),
        }

        trends: List[DetectedTrend] = []

        if len(items) >= 10:
            trends.append(
                DetectedTrend(
                    trend_type="VOL_GROWTH",
                    description=(
                        f"Total volume of {len(items)} complaints indicates"
                        " growing user impact."
                    ),
                    severity="Medium",
                )
            )

        if peak_count >= 5:
            trends.append(
                DetectedTrend(
                    trend_type="SPIKE",
                    description=(
                        f"Sudden complaint spike detected at {peak_hour} with"
                        f" {peak_count} reports in 1 hour."
                    ),
                    severity="High",
                )
            )

        if not trends:
            trends.append(
                DetectedTrend(
                    trend_type="RECURRING",
                    description="Low frequency recurring complaints observed.",
                    severity="Low",
                )
            )

        return stats, trends
