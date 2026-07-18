from typing import Dict, List, Tuple
import structlog

from sentinel_api.ai.agents.metrics_agent.schemas import (
    MetricAnomaly,
    MetricPoint,
    MetricStats,
)
from sentinel_api.ai.agents.metrics_agent.utils import parse_timestamp

logger = structlog.get_logger("sentinel_api.ai.agents.metrics_agent.trend_detector")


class TrendDetector:
    """Detects gradual drift, sudden spikes/drops, and recovery trends."""

    def detect_trends(
        self,
        grouped_points: Dict[Tuple[str, frozenset], List[MetricPoint]],
        stats_dict: Dict[Tuple[str, frozenset], MetricStats],
    ) -> List[MetricAnomaly]:
        """Performs trend line analysis to spot operational anomalies."""
        logger.info("Executing trend detection scan")
        anomalies: List[MetricAnomaly] = []

        for key, points in grouped_points.items():
            if len(points) < 3:
                continue

            name, labels = key
            name_lower = name.lower()
            sorted_pts = sorted(
                points, key=lambda x: parse_timestamp(x.timestamp)
            )
            stats = stats_dict.get(key)
            if not stats:
                continue

            values = [p.value for p in sorted_pts]
            first_val = values[0]
            last_val = values[-1]

            # 1. Gradual upward drift (e.g., memory leak or queue build-up)
            if (
                "mem" in name_lower
                or "latency" in name_lower
                or "queue" in name_lower
            ):
                if last_val > first_val * 1.20 and stats.rate_of_change > 0:
                    increases = sum(
                        1
                        for i in range(len(values) - 1)
                        if values[i + 1] > values[i]
                    )
                    if increases / (len(values) - 1) >= 0.7:
                        anomalies.append(
                            MetricAnomaly(
                                metric_name=name,
                                type="DRIFT",
                                description=(
                                    "Gradual upward trend detected: values climbed"
                                    f" from {first_val} to {last_val} (rate:"
                                    f" {stats.rate_of_change}/min). Potential memory"
                                    " leak or queue build-up."
                                ),
                                severity=(
                                    "High"
                                    if "mem" in name_lower
                                    or "queue" in name_lower
                                    else "Medium"
                                ),
                                labels=dict(labels),
                                timestamp=sorted_pts[-1].timestamp,
                            )
                        )

            # 2. Sudden spikes/drops
            for i in range(1, len(values)):
                prev = values[i - 1]
                curr = values[i]
                delta = curr - prev
                abs_delta = abs(delta)

                if (
                    prev > 0
                    and curr > prev * 2.0
                    and abs_delta > stats.std_dev * 2.0
                ):
                    anomalies.append(
                        MetricAnomaly(
                            metric_name=name,
                            type="SPIKE",
                            description=(
                                f"Sudden metric spike: value jumped from {prev}"
                                f" to {curr} (+{((curr-prev)/prev)*100:.1f}%"
                                " change)."
                            ),
                            severity=(
                                "High"
                                if "error" in name_lower
                                or "latency" in name_lower
                                or "cpu" in name_lower
                                else "Medium"
                            ),
                            labels=dict(labels),
                            timestamp=sorted_pts[i].timestamp,
                        )
                    )
                elif (
                    curr > 0
                    and prev > curr * 2.5
                    and abs_delta > stats.std_dev * 2.0
                ):
                    anomalies.append(
                        MetricAnomaly(
                            metric_name=name,
                            type="DROP",
                            description=(
                                f"Sudden metric drop: value fell from {prev}"
                                f" to {curr} (-{((prev-curr)/prev)*100:.1f}%"
                                " change)."
                            ),
                            severity=(
                                "High"
                                if "throughput" in name_lower
                                or "rate" in name_lower
                                or "hit" in name_lower
                                else "Medium"
                            ),
                            labels=dict(labels),
                            timestamp=sorted_pts[i].timestamp,
                        )
                    )

            # 3. Recovery Trends
            if len(values) >= 5:
                recent = values[-3:]
                older = values[:-3]
                older_mean = sum(older) / len(older)

                if (
                    max(older) > older_mean
                    and recent[2] < recent[1] < recent[0]
                    and recent[2] <= older_mean * 1.1
                ):
                    anomalies.append(
                        MetricAnomaly(
                            metric_name=name,
                            type="RECOVERY",
                            description=(
                                f"Recovery trend detected: metric stabilizing back"
                                f" to baseline ({recent[2]} from peak"
                                f" {max(values)})."
                            ),
                            severity="Informational",
                            labels=dict(labels),
                            timestamp=sorted_pts[-1].timestamp,
                        )
                    )

        return anomalies
