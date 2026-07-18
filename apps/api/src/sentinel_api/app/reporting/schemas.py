from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ReportMetadata(BaseModel):
    """Metadata detailing the incident ID, timestamp, and ownership footprint."""

    incident_id: str = Field(..., description="Target incident ID")
    severity: str = Field(..., description="Incident severity level (e.g. SEV1)")
    status: str = Field(..., description="Incident status (e.g. active)")
    created_at: str = Field(..., description="Incident creation timestamp")
    owner: str = Field(..., description="Owning team handle name")
    affected_services: List[str] = Field(
        default_factory=list, description="List of affected microservices"
    )


class ReportExecutiveSummary(BaseModel):
    """Executive-level narrative of the system regression and its business context."""

    incident_overview: str = Field(..., description="Plain-language description")
    affected_services: List[str] = Field(
        default_factory=list, description="Services impacted"
    )
    severity: str = Field(..., description="Severity level")
    business_impact: str = Field(..., description="Business translation summary")
    investigation_status: str = Field(..., description="Status check of resolution steps")


class TimelineEvent(BaseModel):
    """A chronologically sorted indicator event."""

    timestamp: str = Field(..., description="ISO timestamp")
    event_type: str = Field(..., description="Category: e.g. DEPLOYMENT, LOG, METRICS")
    description: str = Field(..., description="Text description of what occurred")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Custom dictionary fields"
    )


class EvidenceSummary(BaseModel):
    """Evidence categorized by source types."""

    logs: List[str] = Field(
        default_factory=list, description="Error log pattern listings"
    )
    metrics: List[str] = Field(
        default_factory=list, description="Metric anomaly listings"
    )
    deployments: List[str] = Field(
        default_factory=list, description="Correlated deployment events"
    )
    customer_feedback: List[str] = Field(
        default_factory=list, description="User complaints/tickets summaries"
    )


class RootCauseSection(BaseModel):
    """Hypothesis assessment details from Root Cause Agent."""

    primary_root_cause: str = Field(..., description="Most likely cause of incident")
    supporting_evidence: List[str] = Field(
        default_factory=list, description="Direct supporting telemetry facts"
    )
    alternative_hypotheses: List[Dict[str, Any]] = Field(
        default_factory=list, description="Secondary causes ranked by score"
    )
    confidence: float = Field(..., description="Diagnosis confidence rating")


class RecommendationSection(BaseModel):
    """Prioritized response recommendations from Recommendation Agent."""

    immediate_actions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Actions to deploy right away"
    )
    short_term_actions: List[Dict[str, Any]] = Field(
        default_factory=list, description="Actions to execute in minutes"
    )
    long_term_improvements: List[Dict[str, Any]] = Field(
        default_factory=list, description="Follow-up configuration reviews"
    )
    priority: str = Field(..., description="Recommendation priority")
    risk: str = Field(..., description="Mitigation safety rating")


class RecoveryPlanSection(BaseModel):
    """Step-by-step mitigation execution sequence and monitoring steps."""

    recovery_checklist: List[str] = Field(
        default_factory=list, description="Task items checklist"
    )
    validation_steps: List[Dict[str, Any]] = Field(
        default_factory=list, description="Pre-execution command steps"
    )
    monitoring_plan: Dict[str, Any] = Field(
        default_factory=dict, description="Recovery verify metrics"
    )


class ConfidenceSummarySection(BaseModel):
    """Reasoning confidence analytics calculated across the pipeline."""

    overall_confidence: float = Field(..., description="Aggregated confidence rating")
    evidence_quality: float = Field(..., description="Telemetry source quality score")
    coverage_score: float = Field(..., description="Proportion of successful agent runs")
    agent_confidence_summary: Dict[str, float] = Field(
        default_factory=dict, description="Confidence ratings per sub-agent"
    )


class IncidentReport(BaseModel):
    """Consolidated Incident Report containing metadata, timelines, and mitigations."""

    metadata: ReportMetadata = Field(..., description="Incident footprint metadata")
    executive_summary: ReportExecutiveSummary = Field(
        ..., description="Incident overview"
    )
    timeline: List[TimelineEvent] = Field(
        default_factory=list, description="Chronological timeline list"
    )
    evidence: EvidenceSummary = Field(..., description="Grouped evidence list")
    root_cause: RootCauseSection = Field(..., description="Deductions section")
    recommendations: RecommendationSection = Field(
        ..., description="Recommended actions"
    )
    recovery_plan: RecoveryPlanSection = Field(
        ..., description="Recovery check plan"
    )
    confidence: ConfidenceSummarySection = Field(
        ..., description="Aggregated confidence scores"
    )
    raw_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="General metadata details"
    )

