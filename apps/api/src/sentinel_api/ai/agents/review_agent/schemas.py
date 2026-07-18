from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ReviewItem(BaseModel):
    """Represents a standardized customer ticket, review, issue, or Slack message."""

    id: str = Field(..., description="Unique ID of the review/ticket")
    source: str = Field(
        ...,
        description="Source channel: Support Ticket, Review, Chat, Email, GitHub",
    )
    content: str = Field(..., description="Raw feedback text content")
    timestamp: str = Field(..., description="ISO 8601 timestamp of feedback")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata specific to the source"
    )


class ReviewFinding(BaseModel):
    """A structured finding representing clustered feedback issues."""

    category: str = Field(..., description="Issue category (e.g. Authentication)")
    severity: str = Field(..., description="Estimated severity: Info, Low, Medium, High, Critical")
    mentions: int = Field(..., description="Number of reports in this category")
    affected_features: List[str] = Field(
        default_factory=list, description="Extracted features/services affected"
    )
    sample_reports: List[str] = Field(
        default_factory=list, description="Examples of user report snippets"
    )
    confidence: float = Field(
        ..., description="Categorization/clustering confidence [0.0 - 1.0]"
    )
    summary: str = Field(..., description="Text summary of the issue findings")


class DetectedTrend(BaseModel):
    """A trend identified over the customer feedback timeline."""

    trend_type: str = Field(..., description="Type of trend: SPIKE, VOL_GROWTH, RECURRING, NEW_CATEGORY")
    description: str = Field(..., description="Text details of the detected trend")
    severity: str = Field(..., description="Trend severity: Low, Medium, High, Critical")


class ReviewSummary(BaseModel):
    """A structured textual overview of the feedback audit results."""

    executive_summary: str = Field(..., description="High-level narrative summary")
    detailed_findings: str = Field(..., description="Specific issues and categories")
    user_impact_summary: str = Field(..., description="How users are affected")
    business_impact_summary: str = Field(..., description="Business operational threat description")
    potential_contributors: List[str] = Field(
        default_factory=list, description="Possible contributing factors"
    )


class ReviewAgentOutput(BaseModel):
    """The complete result output structure returned by the Review Agent."""

    agent_name: str = Field(..., description="Name of the executing agent")
    execution_time_ms: float = Field(..., description="Execution duration")
    status: str = Field(..., description="Outcome of the agent run")
    confidence: float = Field(..., description="Confidence rating of final outputs")
    findings: List[ReviewFinding] = Field(
        default_factory=list, description="Structured feedback findings"
    )
    detected_trends: List[DetectedTrend] = Field(
        default_factory=list, description="Timely trends identified"
    )
    issue_categories: List[str] = Field(
        default_factory=list, description="Categorized list of issues"
    )
    summary: ReviewSummary = Field(..., description="Text summaries")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata metrics"
    )
