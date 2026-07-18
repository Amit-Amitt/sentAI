from typing import Any, Dict, List
from pydantic import BaseModel, Field


class MetricPoint(BaseModel):
    """A standardized individual metric data point in a time-series."""

    name: str = Field(..., description="Name of the metric (e.g. cpu_usage, latency)")
    value: float = Field(..., description="Numerical value of the metric point")
    timestamp: str = Field(..., description="ISO 8601 timestamp string")
    labels: Dict[str, str] = Field(
        default_factory=dict, description="Metadata dimensions (service, host, etc.)"
    )


class MetricFinding(BaseModel):
    """Structured observation summarizing metric behavior over a timeframe."""

    metric_name: str = Field(..., description="Name of the evaluated metric")
    category: str = Field(
        ..., description="Standardized health category (e.g., CPU, MEMORY, NETWORK)"
    )
    severity: str = Field(
        ...,
        description="Severity rating: Critical, High, Medium, Low, Informational",
    )
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    summary: str = Field(..., description="Textual explanation of the findings")
    occurrences: int = Field(
        ..., description="Number of times abnormal behavior was observed"
    )
    timestamp_start: str = Field(..., description="ISO 8601 start window")
    timestamp_end: str = Field(..., description="ISO 8601 end window")


class MetricAnomaly(BaseModel):
    """A specific detected metric anomaly instance."""

    metric_name: str = Field(..., description="Name of the metric")
    type: str = Field(
        ..., description="Anomaly classification (SPIKE, DROP, DRIFT, BREACH)"
    )
    description: str = Field(..., description="Detailed description of the anomaly")
    severity: str = Field(..., description="Normalized severity rating")
    labels: Dict[str, str] = Field(
        default_factory=dict, description="Metric dimension tags"
    )
    timestamp: str = Field(..., description="ISO 8601 timestamp of occurrence")


class MetricStats(BaseModel):
    """Aggregated statistical telemetry calculations for a metrics time-series."""

    mean: float = Field(..., description="Arithmetic mean value")
    max: float = Field(..., description="Maximum value")
    min: float = Field(..., description="Minimum value")
    p95: float = Field(..., description="95th percentile value")
    std_dev: float = Field(..., description="Standard deviation")
    rate_of_change: float = Field(
        ..., description="Rate of value change over duration"
    )


class MetricsSummary(BaseModel):
    """Summary statements compiled from metrics processing."""

    short_summary: str = Field(..., description="Brief summary sentence")
    detailed_summary: str = Field(..., description="Detailed analysis description")
    health_assessment: str = Field(..., description="Overall system health rating")
    key_metric_changes: List[str] = Field(
        default_factory=list, description="Key operational metric shifts observed"
    )
    potential_contributors: List[str] = Field(
        default_factory=list,
        description="Potential system factors contributing to issues",
    )


class MetricsProcessingStats(BaseModel):
    """Internal processing performance and observation counts."""

    points_parsed: int = Field(..., description="Total time-series points parsed")
    anomalies_detected: int = Field(..., description="Total anomalies identified")
    correlation_groups_count: int = Field(
        ..., description="Count of distinct correlated groups"
    )
    execution_time_ms: float = Field(..., description="Module execution duration")


class MetricsAgentOutput(BaseModel):
    """The final compiled response model produced by the Metrics Agent."""

    agent_name: str = Field(..., description="Name of the executing agent")
    status: str = Field(..., description="Operation outcome (e.g. SUCCESS)")
    execution_time_ms: float = Field(..., description="Latency of execution")
    confidence: float = Field(..., description="Aggregate confidence rating")
    findings: List[MetricFinding] = Field(
        default_factory=list, description="Aggregated metric findings"
    )
    detected_anomalies: List[MetricAnomaly] = Field(
        default_factory=list, description="Individual metric anomalies"
    )
    summary: MetricsSummary = Field(
        ..., description="Summarized analysis blocks"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Execution and system metadata"
    )
    statistics: MetricsProcessingStats = Field(
        ..., description="Telemetry processing stats"
    )
