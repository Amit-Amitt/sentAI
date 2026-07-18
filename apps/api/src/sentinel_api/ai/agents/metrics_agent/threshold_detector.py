from typing import List
import structlog

from sentinel_api.ai.agents.metrics_agent.schemas import MetricAnomaly, MetricPoint

logger = structlog.get_logger("sentinel_api.ai.agents.metrics_agent.threshold_detector")

THRESHOLDS = {
    "cpu": (80.0, 90.0, False),
    "mem": (80.0, 90.0, False),
    "disk": (85.0, 95.0, False),
    "error_rate": (0.02, 0.05, False),
    "latency": (1000.0, 3000.0, False),
    "response_time": (1000.0, 3000.0, False),
    "restart": (0.1, 2.0, False),
    "queue": (100.0, 500.0, False),
    "conn": (80.0, 150.0, False),
    "cache_hit": (0.7, 0.5, True),
}


class ThresholdDetector:
    """Flags data points violating configured operational limits."""

    def detect_breaches(self, points: List[MetricPoint]) -> List[MetricAnomaly]:
        """Scans list of MetricPoints for limit breaches."""
        logger.info("Detecting metric threshold violations")
        anomalies: List[MetricAnomaly] = []

        for pt in points:
            name_lower = pt.name.lower()

            matched_key = None
            for key in THRESHOLDS:
                if key in name_lower:
                    matched_key = key
                    break

            if not matched_key:
                continue

            warn, crit, is_lower = THRESHOLDS[matched_key]

            # Normalize fractional inputs for resource usages
            val = pt.value
            if matched_key in ["cpu", "mem", "disk"] and val <= 1.0:
                val = val * 100.0

            if is_lower:
                if val <= crit:
                    anomalies.append(
                        self._create_anomaly(
                            pt, "Critical", crit, "lower limit violation"
                        )
                    )
                elif val <= warn:
                    anomalies.append(
                        self._create_anomaly(
                            pt, "Warning", warn, "lower limit warning"
                        )
                    )
            else:
                if val >= crit:
                    anomalies.append(
                        self._create_anomaly(
                            pt, "Critical", crit, "upper limit violation"
                        )
                    )
                elif val >= warn:
                    anomalies.append(
                        self._create_anomaly(
                            pt, "Warning", warn, "upper limit warning"
                        )
                    )

        return anomalies

    def _create_anomaly(
        self, pt: MetricPoint, severity: str, limit: float, reason: str
    ) -> MetricAnomaly:
        return MetricAnomaly(
            metric_name=pt.name,
            type="BREACH",
            description=(
                f"Threshold breach: value {pt.value} violated {reason} limit of"
                f" {limit}."
            ),
            severity=severity,
            labels=pt.labels,
            timestamp=pt.timestamp,
        )
