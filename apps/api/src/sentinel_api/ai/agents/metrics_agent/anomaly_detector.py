from typing import Dict, List, Tuple
import structlog

from sentinel_api.ai.agents.metrics_agent.schemas import (
    MetricAnomaly,
    MetricPoint,
    MetricStats,
)

logger = structlog.get_logger("sentinel_api.ai.agents.metrics_agent.anomaly_detector")


class StatisticalAnomalyDetector:
    """Detects statistical outliers in metric streams using Z-score calculation."""

    def detect_anomalies(
        self,
        grouped_points: Dict[Tuple[str, frozenset], List[MetricPoint]],
        stats_dict: Dict[Tuple[str, frozenset], MetricStats],
    ) -> List[MetricAnomaly]:
        """Flags individual points deviating significantly from the series mean."""
        logger.info("Executing statistical Z-score outlier scan")
        anomalies: List[MetricAnomaly] = []

        for key, points in grouped_points.items():
            stats = stats_dict.get(key)
            if not stats or len(points) < 3:
                continue

            name, labels = key
            name_lower = name.lower()

            std_dev = stats.std_dev
            mean = stats.mean

            if std_dev > 0.001:
                for pt in points:
                    z_score = (pt.value - mean) / std_dev
                    if abs(z_score) > 3.0:
                        anomalies.append(
                            MetricAnomaly(
                                metric_name=name,
                                type="OUTLIER",
                                description=(
                                    "Statistical outlier detected: value"
                                    f" {pt.value} deviated from mean {mean} by"
                                    f" Z-score of {z_score:.2f} (std_dev={std_dev})."
                                ),
                                severity=(
                                    "High"
                                    if "error" in name_lower
                                    or "latency" in name_lower
                                    else "Medium"
                                ),
                                labels=dict(labels),
                                timestamp=pt.timestamp,
                            )
                        )

        return anomalies
