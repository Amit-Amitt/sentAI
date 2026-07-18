from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LogFinding(BaseModel):
    """Structured evidence representing an analyzed pattern of logs."""

    category: str = Field(..., description="The detected error/log type category")
    severity: str = Field(..., description="Normalized severity: Critical, High, Medium, Low, Informational")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")
    summary: str = Field(..., description="Short explanation of the finding")
    occurrences: int = Field(..., description="Count of log lines matching this pattern")
    sample_log: str = Field(..., description="A concrete representative log line")
    timestamp_start: str = Field(..., description="ISO 8601 start time of matching logs")
    timestamp_end: str = Field(..., description="ISO 8601 end time of matching logs")


class LogSummary(BaseModel):
    """The structured textual narrative summarizing the overall log analysis outcome."""

    short_summary: str = Field(..., description="A concise single-sentence summary")
    detailed_summary: str = Field(..., description="A comprehensive summary of the observations")
    key_observations: List[str] = Field(
        default_factory=list, description="List of key points identified during investigation"
    )
    potential_contributors: List[str] = Field(
        default_factory=list, description="Possible contributing factors or trigger events"
    )


class LogProcessingStats(BaseModel):
    """Technical telemetry on the execution of log parsing."""

    lines_parsed: int = Field(..., description="Total log lines evaluated")
    anomalies_detected: int = Field(..., description="Count of individual anomalies flagged")
    error_clusters_count: int = Field(..., description="Count of unique error groups clustered")
    execution_time_ms: float = Field(..., description="Time taken to process the log file in ms")


class LogAgentOutput(BaseModel):
    """Structured report returned by the Log Agent to the Coordinator."""

    agent_name: str = Field(default="Log Agent", description="Name of the executing agent")
    execution_time_ms: float = Field(..., description="Total processing time in ms")
    status: str = Field(..., description="Result status: SUCCESS, PARTIAL_SUCCESS, FAILED")
    confidence: float = Field(..., description="Overall confidence level of log findings")
    findings: List[LogFinding] = Field(
        default_factory=list, description="Analyzed list of structured findings/evidence"
    )
    summary: LogSummary = Field(..., description="Structured summary narrative of log analysis")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extracted environment/service metadata context"
    )
    statistics: LogProcessingStats = Field(
        ..., description="Telemetry statistics from parsing pipeline execution"
    )
