from typing import Any, Dict, List, Tuple
import structlog

from sentinel_api.ai.agents.metrics_agent.schemas import (
    MetricAnomaly,
    MetricFinding,
    MetricStats,
    MetricsSummary,
)

logger = structlog.get_logger("sentinel_api.ai.agents.metrics_agent.summarizer")


class MetricsSummarizer:
    """Aggregates metrics findings and anomalies into operational summaries."""

    def summarize(
        self,
        findings: List[MetricFinding],
        anomalies: List[MetricAnomaly],
        stats_dict: Dict[Tuple[str, frozenset], MetricStats],
        total_points: int,
    ) -> MetricsSummary:
        """Constructs health assessments, summaries, and potential root factors."""
        logger.info("Generating metrics analysis summaries")

        critical_count = sum(1 for f in findings if f.severity == "Critical")
        high_count = sum(1 for f in findings if f.severity == "High")

        # 1. Short Summary
        short_summary = (
            f"Metrics analysis processed {total_points} data points. "
            f"Detected {len(anomalies)} anomaly events and consolidated them into"
            f" {len(findings)} findings ({critical_count} Critical,"
            f" {high_count} High)."
        )

        # 2. Detailed Summary
        services = set()
        for a in anomalies:
            svc = a.labels.get("service")
            if svc:
                services.add(svc)

        svc_str = (
            f" across service(s): {', '.join(sorted(list(services)))}"
            if services
            else ""
        )

        detailed_summary = (
            "The monitoring stream was checked for threshold limits, statistical"
            f" drift, and sudden spikes/drops{svc_str}. Out of"
            f" {len(stats_dict)} unique time-series, {len(findings)} distinct"
            " clusters of abnormal behavior were flagged. The primary issues are"
            " documented in the key observations below."
        )

        # 3. Health Assessment
        if critical_count > 0:
            health_assessment = (
                "CRITICAL - Severe resource saturation or error rate threshold"
                " breaches detected."
            )
        elif high_count > 0:
            health_assessment = (
                "DEGRADED - High latency, resource usage spikes, or statistical"
                " outliers observed."
            )
        elif len(anomalies) > 0:
            health_assessment = (
                "WARNING - Minor warnings or gradual metrics drift detected."
            )
        else:
            health_assessment = (
                "HEALTHY - All analyzed metrics are within normal operational"
                " limits."
            )

        # 4. Key Metric Changes
        key_metric_changes: List[str] = []
        for f in findings:
            key_metric_changes.append(f"[{f.severity}] {f.summary}")

        if not key_metric_changes:
            key_metric_changes.append(
                "No significant metric variations or anomalies were registered."
            )

        # 5. Potential Contributors
        potential_contributors: List[str] = []
        categories = set()
        for f in findings:
            categories.update(c.strip() for c in f.category.split(","))

        if "CPU" in categories or "MEMORY" in categories or "DISK" in categories:
            potential_contributors.append(
                "Workload surge, memory leak, or unoptimized application process"
                " cycles."
            )
        if "ERROR" in categories:
            potential_contributors.append(
                "Recent code deployments, external dependencies outages, or"
                " authentication issues."
            )
        if "LATENCY" in categories:
            potential_contributors.append(
                "Database lock congestion, downstream network packet loss, or"
                " thread/connection pool exhaustion."
            )
        if "QUEUE" in categories:
            potential_contributors.append(
                "Worker node failures, slow consumer performance, or queue"
                " serialization lags."
            )
        if "CACHE" in categories:
            potential_contributors.append(
                "Cache eviction storms, high invalidation rates, or cache server"
                " capacity limits."
            )

        if not potential_contributors:
            potential_contributors.append(
                "Operational baseline is normal. No metric anomalies suggesting"
                " system distress."
            )

        return MetricsSummary(
            short_summary=short_summary,
            detailed_summary=detailed_summary,
            health_assessment=health_assessment,
            key_metric_changes=key_metric_changes,
            potential_contributors=potential_contributors,
        )
