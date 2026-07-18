import time
from typing import Any, Dict
import structlog

from sentinel_api.ai.agents.metrics_agent.analyzer import MetricsAnalyzer
from sentinel_api.ai.agents.metrics_agent.collector import MetricsCollector
from sentinel_api.ai.agents.metrics_agent.schemas import (
    MetricsAgentOutput,
    MetricsProcessingStats,
)
from sentinel_api.ai.agents.metrics_agent.summarizer import MetricsSummarizer
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import AgentRequest

logger = structlog.get_logger("sentinel_api.ai.agents.metrics_agent.metrics_agent")


class MetricsAgent(BaseAgent):
    """Orchestrator agent for checking monitoring metrics for anomalies and trends."""

    def __init__(self) -> None:
        super().__init__(name="Metrics Agent")
        self.collector = MetricsCollector()
        self.analyzer = MetricsAnalyzer()
        self.summarizer = MetricsSummarizer()

    def validate(self, request: AgentRequest) -> None:
        """Ensures telemetry payload is present inside request signals or inputs."""
        super().validate(request)

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        metrics = (
            signals.get("metrics")
            or signals.get("raw_metrics")
            or inputs.get("metrics")
            or inputs.get("raw_metrics")
        )

        if not metrics:
            raise AgentException("Metrics data is missing or empty in signals/inputs.")

    async def _run(
        self, request: AgentRequest, config: ModelConfig
    ) -> Dict[str, Any]:
        """Collects, analyzes, correlates and summarizes time-series metrics data."""
        start_time = time.perf_counter()

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        raw_metrics = (
            signals.get("metrics")
            or signals.get("raw_metrics")
            or inputs.get("metrics")
            or inputs.get("raw_metrics")
        )

        # 1. Collect points
        points = self.collector.collect(raw_metrics)
        total_points = len(points)

        # 2. Analyze
        findings, anomalies, stats_dict, correlation_groups = (
            self.analyzer.analyze(points)
        )

        # 3. Summarize
        summary = self.summarizer.summarize(
            findings, anomalies, stats_dict, total_points
        )

        # 4. Confidence Calculation
        base_confidence = 0.85
        high_severity_anomalies = sum(
            1 for a in anomalies if a.severity in ["Critical", "High"]
        )
        base_confidence -= min(0.20, high_severity_anomalies * 0.04)
        if correlation_groups > 0:
            base_confidence += min(0.15, correlation_groups * 0.05)
        overall_confidence = round(max(0.1, min(1.0, base_confidence)), 2)

        # 5. Metadata Compilation
        services = set()
        hosts = set()
        for pt in points:
            if pt.labels.get("service"):
                services.add(pt.labels["service"])
            if pt.labels.get("host"):
                hosts.add(pt.labels["host"])

        metadata = {
            "services": sorted(list(services)),
            "hosts": sorted(list(hosts)),
            "metric_names": sorted(list({pt.name for pt in points})),
            "timestamp_start": min((pt.timestamp for pt in points), default=""),
            "timestamp_end": max((pt.timestamp for pt in points), default=""),
        }

        # 6. Statistics
        duration_ms = (time.perf_counter() - start_time) * 1000
        statistics = MetricsProcessingStats(
            points_parsed=total_points,
            anomalies_detected=len(anomalies),
            correlation_groups_count=correlation_groups,
            execution_time_ms=duration_ms,
        )

        output = MetricsAgentOutput(
            agent_name=self.name,
            status="SUCCESS" if total_points > 0 else "PARTIAL_SUCCESS",
            execution_time_ms=duration_ms,
            confidence=overall_confidence,
            findings=findings,
            detected_anomalies=anomalies,
            summary=summary,
            metadata=metadata,
            statistics=statistics,
        )

        result_dict = output.model_dump()
        result_dict["reasoning_summary"] = summary.short_summary
        return result_dict
