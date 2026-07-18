from typing import Dict, List, Tuple
import structlog

from sentinel_api.ai.agents.metrics_agent.anomaly_detector import (
    StatisticalAnomalyDetector,
)
from sentinel_api.ai.agents.metrics_agent.schemas import (
    MetricAnomaly,
    MetricFinding,
    MetricPoint,
    MetricStats,
)
from sentinel_api.ai.agents.metrics_agent.statistics import MetricStatsCalculator
from sentinel_api.ai.agents.metrics_agent.threshold_detector import (
    ThresholdDetector,
)
from sentinel_api.ai.agents.metrics_agent.trend_detector import TrendDetector
from sentinel_api.ai.agents.metrics_agent.utils import parse_timestamp

logger = structlog.get_logger("sentinel_api.ai.agents.metrics_agent.analyzer")


class MetricsAnalyzer:
    """Orchestrates statistics, threshold, trend checks and correlates concurrent anomalies."""

    def __init__(self) -> None:
        self.stats_calculator = MetricStatsCalculator()
        self.threshold_detector = ThresholdDetector()
        self.trend_detector = TrendDetector()
        self.anomaly_detector = StatisticalAnomalyDetector()

    def analyze(
        self, points: List[MetricPoint]
    ) -> Tuple[
        List[MetricFinding],
        List[MetricAnomaly],
        Dict[Tuple[str, frozenset], MetricStats],
        int,
    ]:
        """Runs the telemetry evaluation pipelines and outputs consolidated findings."""
        logger.info("Executing comprehensive metrics analysis")

        # 1. Group points by metric dimensions
        grouped: Dict[Tuple[str, frozenset], List[MetricPoint]] = {}
        for pt in points:
            key = (pt.name, frozenset(pt.labels.items()))
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(pt)

        # 2. Compute statistics
        stats_dict = self.stats_calculator.compute_stats(grouped)

        # 3. Detect anomalies across layers
        anomalies: List[MetricAnomaly] = []
        anomalies.extend(self.threshold_detector.detect_breaches(points))
        anomalies.extend(self.trend_detector.detect_trends(grouped, stats_dict))
        anomalies.extend(self.anomaly_detector.detect_anomalies(grouped, stats_dict))

        # 4. Correlate dimensional anomalies
        findings, correlation_groups = self._correlate_anomalies(anomalies)

        return findings, anomalies, stats_dict, correlation_groups

    def _correlate_anomalies(
        self, anomalies: List[MetricAnomaly]
    ) -> Tuple[List[MetricFinding], int]:
        """Groups anomalies sharing timestamp alignment and label signatures."""
        if not anomalies:
            return [], 0

        sorted_anoms = sorted(
            anomalies, key=lambda x: parse_timestamp(x.timestamp)
        )
        clusters: List[List[MetricAnomaly]] = []

        for anom in sorted_anoms:
            ts = parse_timestamp(anom.timestamp)
            service = anom.labels.get("service")
            host = anom.labels.get("host")

            placed = False
            for cluster in clusters:
                last_in_cluster = cluster[-1]
                last_ts = parse_timestamp(last_in_cluster.timestamp)

                time_ok = abs((ts - last_ts).total_seconds()) <= 120.0

                label_ok = False
                if service and last_in_cluster.labels.get("service") == service:
                    label_ok = True
                elif host and last_in_cluster.labels.get("host") == host:
                    label_ok = True
                elif (
                    not service
                    and not host
                    and not anom.labels
                    and not last_in_cluster.labels
                ):
                    label_ok = True

                if time_ok and label_ok:
                    cluster.append(anom)
                    placed = True
                    break

            if not placed:
                clusters.append([anom])

        findings: List[MetricFinding] = []
        correlation_groups_count = 0

        for cluster in clusters:
            is_correlated = len(cluster) > 1
            if is_correlated:
                correlation_groups_count += 1

            first = cluster[0]
            last = cluster[-1]

            severities = [c.severity for c in cluster]
            final_severity = "Informational"
            for s in [
                "Critical",
                "High",
                "Warning",
                "Medium",
                "Low",
                "Informational",
            ]:
                if any(
                    x == s or (s == "Medium" and x == "Warning")
                    for x in severities
                ):
                    final_severity = (
                        "Critical"
                        if s == "Critical"
                        else (s if s != "Warning" else "Medium")
                    )
                    break

            categories = {self._guess_category(c.metric_name) for c in cluster}
            final_category = ", ".join(sorted(list(categories)))

            dim_str = ""
            svc = first.labels.get("service")
            h = first.labels.get("host")
            if svc:
                dim_str = f" on service '{svc}'"
            elif h:
                dim_str = f" on host '{h}'"

            if is_correlated:
                anoms_summary = ", ".join(
                    f"{c.type} on {c.metric_name}" for c in cluster[:3]
                )
                if len(cluster) > 3:
                    anoms_summary += f" and {len(cluster)-3} others"
                summary_text = (
                    f"Correlated metric anomalies{dim_str}: {anoms_summary}"
                )
            else:
                summary_text = (
                    f"Metric anomaly{dim_str}: {first.type} detected on"
                    f" '{first.metric_name}' - {first.description}"
                )

            confidence = min(1.0, 0.7 + (len(cluster) - 1) * 0.1)

            findings.append(
                MetricFinding(
                    metric_name=(
                        first.metric_name if not is_correlated else "multi-metrics"
                    ),
                    category=final_category,
                    severity=final_severity,
                    confidence=confidence,
                    summary=summary_text,
                    occurrences=len(cluster),
                    timestamp_start=first.timestamp,
                    timestamp_end=last.timestamp,
                )
            )

        return findings, correlation_groups_count

    def _guess_category(self, name: str) -> str:
        name_lower = name.lower()
        for cat in [
            "cpu",
            "memory",
            "disk",
            "network",
            "latency",
            "error",
            "queue",
            "connection",
            "restart",
            "throughput",
            "cache",
        ]:
            if cat in name_lower:
                return cat.upper()
        return "SYSTEM"
