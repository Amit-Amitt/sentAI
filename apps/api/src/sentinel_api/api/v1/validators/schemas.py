from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IncidentAnalyzeRequest(BaseModel):
    """Payload validator for starting an incident investigation."""

    incident_id: str = Field(..., description="Unique incident identifier")
    severity: str = Field(..., description="Severity category, e.g. SEV1")
    status: str = Field("active", description="Initial incident status")
    summary: str = Field(..., description="Short text summary of the issue")
    logs: Optional[Any] = Field(
        None, description="Optional raw or structured logs"
    )
    metrics: Optional[Any] = Field(
        None, description="Optional raw or structured metrics"
    )
    deployment_history: Optional[Any] = Field(
        None, description="Optional deployment history records"
    )
    customer_reports: Optional[Any] = Field(
        None, description="Optional customer reports / reviews"
    )


class CoordinatorRunRequest(BaseModel):
    """Payload validator for manual coordinator invocation."""

    incident_context: Dict[str, Any] = Field(
        ..., description="Incident context fields"
    )
    execution_context: Dict[str, Any] = Field(
        ..., description="Execution context attributes"
    )
    inputs: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Custom coordinator input keys"
    )


class AgentRunRequest(BaseModel):
    """Payload validator for single agent execution routes."""

    incident_context: Dict[str, Any] = Field(
        ..., description="Incident context fields"
    )
    execution_context: Dict[str, Any] = Field(
        ..., description="Execution context attributes"
    )
    inputs: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Custom agent execution parameters"
    )
