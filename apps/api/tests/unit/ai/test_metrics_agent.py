import pytest
from datetime import datetime, UTC, timedelta
from sentinel_api.ai.agents.metrics_agent import MetricsAgent
from sentinel_api.ai.agents.metrics_agent.collector import MetricsCollector
from sentinel_api.ai.agents.metrics_agent.statistics import MetricStatsCalculator
from sentinel_api.ai.agents.metrics_agent.threshold_detector import ThresholdDetector
from sentinel_api.ai.agents.metrics_agent.trend_detector import TrendDetector
from sentinel_api.ai.agents.metrics_agent.anomaly_detector import StatisticalAnomalyDetector
from sentinel_api.ai.agents.metrics_agent.analyzer import MetricsAnalyzer
from sentinel_api.ai.agents.metrics_agent.summarizer import MetricsSummarizer
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.agents.metrics_agent.schemas import MetricPoint
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)


@pytest.fixture
def sample_json_metrics():
    now = datetime.now(UTC)
    return [
        {"name": "cpu_usage", "value": 45.0, "timestamp": (now - timedelta(minutes=10)).isoformat(), "labels": {"service": "api-gateway", "host": "srv-1"}},
        {"name": "cpu_usage", "value": 55.0, "timestamp": (now - timedelta(minutes=5)).isoformat(), "labels": {"service": "api-gateway", "host": "srv-1"}},
        {"name": "cpu_usage", "value": 95.0, "timestamp": now.isoformat(), "labels": {"service": "api-gateway", "host": "srv-1"}},
        {"name": "latency", "value": 150.0, "timestamp": (now - timedelta(minutes=10)).isoformat(), "labels": {"service": "api-gateway", "host": "srv-1"}},
        {"name": "latency", "value": 200.0, "timestamp": (now - timedelta(minutes=5)).isoformat(), "labels": {"service": "api-gateway", "host": "srv-1"}},
        {"name": "latency", "value": 3500.0, "timestamp": now.isoformat(), "labels": {"service": "api-gateway", "host": "srv-1"}},
    ]


@pytest.fixture
def sample_prometheus_metrics():
    return (
        "# HELP cpu_usage CPU utilization\n"
        "# TYPE cpu_usage gauge\n"
        'cpu_usage{service="user-auth",host="srv-2"} 85.5 1784382000\n'
        'cpu_usage{service="user-auth",host="srv-2"} 92.0 1784382300\n'
        'cache_hit_ratio{service="user-auth"} 0.45 1784382300\n'
    )


def test_metrics_collector_json(sample_json_metrics):
    collector = MetricsCollector()
    points = collector.collect(sample_json_metrics)

    assert len(points) == 6
    assert points[0].name == "cpu_usage"
    assert points[0].value == 45.0
    assert points[0].labels["service"] == "api-gateway"


def test_metrics_collector_prometheus(sample_prometheus_metrics):
    collector = MetricsCollector()
    points = collector.collect(sample_prometheus_metrics)

    assert len(points) == 3
    assert points[0].name == "cpu_usage"
    assert points[0].value == 85.5
    assert points[0].labels["service"] == "user-auth"
    assert points[2].name == "cache_hit_ratio"
    assert points[2].value == 0.45


def test_statistics_calculator(sample_json_metrics):
    collector = MetricsCollector()
    calculator = MetricStatsCalculator()

    points = collector.collect(sample_json_metrics)
    grouped = {}
    for pt in points:
        key = (pt.name, frozenset(pt.labels.items()))
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(pt)

    stats = calculator.compute_stats(grouped)
    cpu_key = ("cpu_usage", frozenset([("service", "api-gateway"), ("host", "srv-1")]))
    assert cpu_key in stats
    assert stats[cpu_key].max == 95.0
    assert stats[cpu_key].min == 45.0
    assert stats[cpu_key].mean == 65.0
    # Rate of change: delta of 50 units over 10 minutes = 5.0 units/min
    assert stats[cpu_key].rate_of_change == 5.0


def test_threshold_detector(sample_json_metrics):
    collector = MetricsCollector()
    detector = ThresholdDetector()

    points = collector.collect(sample_json_metrics)
    anomalies = detector.detect_breaches(points)

    # cpu_usage value 95.0 breaches critical upper threshold (90.0)
    # latency value 3500.0 breaches critical upper threshold (3000.0)
    assert len(anomalies) >= 2
    assert any(a.metric_name == "cpu_usage" and a.severity == "Critical" for a in anomalies)
    assert any(a.metric_name == "latency" and a.severity == "Critical" for a in anomalies)


def test_trend_detector():
    # Construct memory leak style linear increase data points
    now = datetime.now(UTC)
    points = [
        MetricPoint(name="memory_usage", value=50.0, timestamp=(now - timedelta(minutes=10)).isoformat(), labels={"service": "user-auth"}),
        MetricPoint(name="memory_usage", value=55.0, timestamp=(now - timedelta(minutes=8)).isoformat(), labels={"service": "user-auth"}),
        MetricPoint(name="memory_usage", value=60.0, timestamp=(now - timedelta(minutes=6)).isoformat(), labels={"service": "user-auth"}),
        MetricPoint(name="memory_usage", value=65.0, timestamp=(now - timedelta(minutes=4)).isoformat(), labels={"service": "user-auth"}),
        MetricPoint(name="memory_usage", value=70.0, timestamp=(now - timedelta(minutes=2)).isoformat(), labels={"service": "user-auth"}),
        MetricPoint(name="memory_usage", value=75.0, timestamp=now.isoformat(), labels={"service": "user-auth"}),
    ]

    grouped = {("memory_usage", frozenset([("service", "user-auth")])): points}
    stats_calculator = MetricStatsCalculator()
    stats = stats_calculator.compute_stats(grouped)

    detector = TrendDetector()
    anomalies = detector.detect_trends(grouped, stats)

    # Should detect memory drift upward
    assert len(anomalies) >= 1
    assert anomalies[0].type == "DRIFT"


def test_statistical_anomaly_detector():
    now = datetime.now(UTC)
    # Add many stable baseline points so that the single outlier has a Z-score > 3.0
    points = [
        MetricPoint(name="latency", value=100.0 + (i % 3 - 1), timestamp=(now - timedelta(minutes=20 - i)).isoformat(), labels={})
        for i in range(15)
    ]
    # Add the outlier
    points.append(MetricPoint(name="latency", value=1000.0, timestamp=now.isoformat(), labels={}))

    grouped = {("latency", frozenset()): points}
    stats = MetricStatsCalculator().compute_stats(grouped)

    detector = StatisticalAnomalyDetector()
    anomalies = detector.detect_anomalies(grouped, stats)

    assert len(anomalies) == 1
    assert anomalies[0].type == "OUTLIER"


def test_analyzer_correlation(sample_json_metrics):
    collector = MetricsCollector()
    analyzer = MetricsAnalyzer()

    points = collector.collect(sample_json_metrics)
    findings, anomalies, stats, correlation_groups = analyzer.analyze(points)

    # cpu_usage and latency spiked concurrently on the same service "api-gateway"
    # They should be grouped into a single correlated finding
    assert len(findings) == 1
    assert findings[0].occurrences >= 2
    assert "Correlated" in findings[0].summary
    assert correlation_groups == 1


def test_summarizer(sample_json_metrics):
    collector = MetricsCollector()
    analyzer = MetricsAnalyzer()
    summarizer = MetricsSummarizer()

    points = collector.collect(sample_json_metrics)
    findings, anomalies, stats, correlation_groups = analyzer.analyze(points)

    summary = summarizer.summarize(findings, anomalies, stats, len(points))
    assert "api-gateway" in summary.detailed_summary
    assert summary.health_assessment.startswith("CRITICAL")
    assert any("latency" in change.lower() for change in summary.key_metric_changes)
    assert any("Workload" in factor for factor in summary.potential_contributors)


@pytest.mark.asyncio
async def test_metrics_agent_end_to_end(sample_json_metrics):
    agent = MetricsAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-metrics-agent-1",
        correlation_id="corr-metrics-agent-2",
        agent_id="test-metrics-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-metrics-agent-3",
        severity="SEV1",
        status="active",
        summary="Latency alerts triggering",
        signals={"raw_metrics": sample_json_metrics}
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)

    assert result.success is True
    assert result.output["agent_name"] == "Metrics Agent"
    assert result.output["status"] == "SUCCESS"
    assert len(result.output["findings"]) == 1
    assert result.output["statistics"]["points_parsed"] == 6
    assert result.output["statistics"]["anomalies_detected"] >= 2
    assert result.confidence > 0.5


@pytest.mark.asyncio
async def test_metrics_agent_validation_failures():
    agent = MetricsAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-metrics-agent-1",
        correlation_id="corr-metrics-agent-2",
        agent_id="test-metrics-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-metrics-agent-3",
        severity="SEV1",
        status="active",
        summary="No metrics details"
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)
    assert result.success is False
    assert "Metrics data is missing" in result.reasoning_summary
