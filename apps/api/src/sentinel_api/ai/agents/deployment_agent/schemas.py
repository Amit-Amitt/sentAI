from typing import Any, Dict, List
from pydantic import BaseModel, Field


class DeploymentEvent(BaseModel):
    """Represents a parsed deployment, configuration update, migration, or release event."""

    deployment_id: str = Field(..., description="Unique ID of the deployment")
    service: str = Field(..., description="Service or application name")
    version: str = Field(..., description="Target release version or commit SHA")
    environment: str = Field(..., description="Deploy target (e.g. prod, staging)")
    timestamp: str = Field(..., description="ISO 8601 timestamp of deployment start")
    change_type: str = Field(
        ..., description="Category of change: APP, CONFIG, FLAG, INFRA, DB"
    )
    status: str = Field(
        ..., description="Deployment outcome: SUCCESS, FAILED, ROLLBACK"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata specific to the change type"
    )


class DeploymentFinding(BaseModel):
    """Structured evidence linking a deployment event to the incident timeline."""

    deployment_id: str = Field(..., description="ID of the correlated deployment")
    version: str = Field(..., description="Software/infrastructure version")
    timestamp: str = Field(..., description="Deployment time")
    affected_services: List[str] = Field(
        default_factory=list, description="Services affected by this change"
    )
    change_type: str = Field(..., description="Type of change category")
    correlation_score: float = Field(
        ..., description="Statistical correlation score [0.0 - 1.0]"
    )
    confidence: float = Field(
        ..., description="Confidence in the link [0.0 - 1.0]"
    )
    summary: str = Field(..., description="Textual correlation explanation")


class DeploymentTimelineEvent(BaseModel):
    """A single node in a chronological release timeline."""

    timestamp: str = Field(..., description="ISO 8601 timestamp of the event")
    event_type: str = Field(..., description="Type of change or lifecycle action")
    description: str = Field(..., description="Brief description of what changed")
    service: str = Field(..., description="Target service affected")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Supplemental details"
    )


class DeploymentSummary(BaseModel):
    """A programmatic textual summary of deployment audit results."""

    short_summary: str = Field(..., description="Brief summary sentence")
    timeline_summary: List[str] = Field(
        default_factory=list, description="Chronological sequence summary strings"
    )
    detected_risks: List[str] = Field(
        default_factory=list, description="Identified high-risk deployment flags"
    )
    key_changes: List[str] = Field(
        default_factory=list, description="Primary code/config changes detected"
    )
    potential_contributors: List[str] = Field(
        default_factory=list, description="Potential contribution reasons"
    )


class DeploymentAgentOutput(BaseModel):
    """Final output result structure returned by the Deployment Agent."""

    agent_name: str = Field(..., description="Name of the executing agent")
    execution_time_ms: float = Field(..., description="Execution duration")
    status: str = Field(..., description="Outcome of the agent execution")
    confidence: float = Field(..., description="Aggregated confidence rating")
    findings: List[DeploymentFinding] = Field(
        default_factory=list, description="Deployment findings correlated with incident"
    )
    deployment_timeline: List[DeploymentTimelineEvent] = Field(
        default_factory=list, description="Chronological deployment events"
    )
    correlated_events: List[DeploymentFinding] = Field(
        default_factory=list, description="Detailed listing of related events"
    )
    summary: DeploymentSummary = Field(
        ..., description="Summary narrative blocks"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Execution and system metadata"
    )
