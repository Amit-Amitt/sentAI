from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ExecutionContext(BaseModel):
    """Shared execution context tracking the lifecycle of an agent run."""

    request_id: str = Field(..., description="HTTP request trace correlation ID")
    correlation_id: str = Field(
        ..., description="Correlation ID spanning multiple agent runs"
    )
    agent_id: str = Field(..., description="Unique name/identifier of the active agent")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of when the execution began",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Timing, execution context logs, and telemetry parameters",
    )


class IncidentContext(BaseModel):
    """Operational incident context details sent to agent investigators."""

    incident_id: str = Field(
        ..., description="Unique database UUID of the target incident"
    )
    severity: str = Field(
        ..., description="Severity level of the incident (e.g. SEV1, SEV2)"
    )
    status: str = Field(..., description="Current state of the incident lifecycle")
    summary: str = Field(
        ..., description="Textual description or alerts triggering the incident"
    )
    signals: dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary containing raw signal streams, logs, or metrics",
    )


class AgentRequest(BaseModel):
    """Standardized input request wrapping parameters to initiate an agent run."""

    execution_context: ExecutionContext = Field(..., description="Tracing parameters")
    incident_context: IncidentContext = Field(
        ..., description="Target incident information"
    )
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional freeform runtime arguments for the agent",
    )


class AgentResult(BaseModel):
    """Unified result container returned by all executing agents in Sentinel AI."""

    success: bool = Field(..., description="Indicator of whether execution succeeded")
    output: Any = Field(
        ..., description="Final output, can be JSON structure or raw text"
    )
    confidence: float = Field(
        ..., description="Confidence score between 0.0 (low) and 1.0 (high)"
    )
    reasoning_summary: str = Field(
        ..., description="Brief summary reasoning behind the output findings"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Token usage, models run, retry counts"
    )
    processing_time_ms: float = Field(
        ..., description="Execution latency in milliseconds"
    )

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence score must reside between 0.0 and 1.0")
        return v


class ToolResult(BaseModel):
    """Standard container encapsulating outcomes of abstract tool invocations."""

    tool_name: str = Field(..., description="Name of the tool that was executed")
    success: bool = Field(
        ..., description="Indicates if execution completed without error"
    )
    output: str = Field(..., description="String output response from the tool")
    error: str | None = Field(
        None, description="Detailed error message if success is False"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Performance latency, execution parameters"
    )
