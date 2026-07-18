from typing import Any, Dict, List
from pydantic import BaseModel, Field


class RecommendedAction(BaseModel):
    """An SRE action item recommended to mitigate or resolve the incident."""

    id: str = Field(..., description="Action ID")
    action_type: str = Field(..., description="Type: e.g. ROLLBACK, RESTART, SCALE")
    title: str = Field(..., description="Short descriptive title of the action")
    description: str = Field(..., description="Step details of the action")
    priority: str = Field(..., description="Priority: Low, Medium, High, Critical")
    urgency: str = Field(..., description="Urgency: Low, Medium, High, Critical")
    execution_order: int = Field(..., description="Execution sequence position index")
    estimated_impact: str = Field(..., description="Text assessment of mitigation effect")
    risk_level: str = Field(..., description="Risk level: Low, Medium, High")
    side_effects: List[str] = Field(
        default_factory=list, description="List of possible side effects"
    )


class RiskAssessment(BaseModel):
    """Incident recovery operational risk metrics."""

    risk_score: float = Field(..., description="Calculated risk score [0.0 - 1.0]")
    potential_side_effects: List[str] = Field(
        default_factory=list, description="General side effects of response plan"
    )
    rollback_difficulty: str = Field(..., description="Rollback complexity: Low, Medium, High")
    business_impact: str = Field(..., description="Estimated business impact: Low, Medium, High")
    confidence: float = Field(..., description="Agent confidence in response safety")


class ValidationCheck(BaseModel):
    """Pre-execution validation steps to verify the readiness/safety of commands."""

    title: str = Field(..., description="Name of validation step")
    command_suggestion: str = Field(..., description="Example shell/api verification command")
    success_criteria: str = Field(..., description="Expected safe return/output criteria")


class RecoveryMonitoringPlan(BaseModel):
    """A list of indicators and durations to verify incident mitigation."""

    metrics_to_watch: List[str] = Field(..., description="Telemetry metrics to observe")
    duration_minutes: int = Field(..., description="Length of observation duration")
    success_criteria: str = Field(..., description="Required system state to close ticket")
    rollback_verification_steps: List[str] = Field(
        default_factory=list, description="Manual check steps if recovery fails"
    )


class RecommendationAgentOutput(BaseModel):
    """The final structured recovery response plan payload."""

    agent_name: str = Field(..., description="Name of the agent")
    execution_time_ms: float = Field(..., description="Time taken to compute recommendations")
    status: str = Field(..., description="Run outcome status")
    confidence: float = Field(..., description="Plan safety confidence score")
    incident_priority: str = Field(..., description="Mitigated incident priority level")
    recommended_actions: List[RecommendedAction] = Field(
        default_factory=list, description="Action sequence"
    )
    execution_order: List[str] = Field(
        default_factory=list, description="Ordered action ID list"
    )
    risk_assessment: RiskAssessment = Field(..., description="Calculated risk factors")
    validation_checklist: List[ValidationCheck] = Field(
        default_factory=list, description="Verification checks"
    )
    recovery_monitoring_plan: RecoveryMonitoringPlan = Field(
        ..., description="Verification monitoring parameters"
    )
    executive_summary: str = Field(..., description="Plain-language recovery summary")
    technical_summary: str = Field(..., description="Detailed engineering recovery description")
    business_summary: str = Field(..., description="Business operational recovery impact")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata summary metrics"
    )
