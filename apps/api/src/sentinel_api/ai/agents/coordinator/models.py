from enum import Enum
from typing import Any, Dict, List
from pydantic import BaseModel, Field

from sentinel_api.ai.schemas.models import AgentResult


class AgentStatus(str, Enum):
    """Representing status transitions of coordinated agents."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ExecutionPlanItem(BaseModel):
    """Defines execution parameters and state for an individual agent in the plan."""

    agent_name: str = Field(..., description="Name of the coordinated agent")
    priority: int = Field(default=1, description="Priority weight (lower runs first)")
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of agent names that must complete before this agent runs",
    )
    status: AgentStatus = Field(
        default=AgentStatus.PENDING, description="Current execution status"
    )
    retries: int = Field(
        default=0, description="Number of execution retries already attempted"
    )
    timeout: float = Field(
        default=30.0, description="Maximum execution timeout in seconds"
    )
    execution_order: int = Field(
        default=0, description="Scheduled batch execution index"
    )


class ExecutionPlan(BaseModel):
    """Contains all execution plan items scheduled by the Coordinator."""

    items: Dict[str, ExecutionPlanItem] = Field(
        default_factory=dict, description="Mapping of agent name to execution item config"
    )


class FinalExecutionState(BaseModel):
    """The structured result containing aggregated reports from all coordinated agents."""

    incident_summary: str = Field(..., description="Summary of the incident context")
    execution_summary: str = Field(
        ..., description="Overall summary of the plan's execution path"
    )
    agent_results: Dict[str, AgentResult] = Field(
        default_factory=dict,
        description="Collected agent results indexed by agent name",
    )
    overall_confidence: float = Field(
        ..., description="Aggregated confidence score across all executed agents"
    )
    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of execution errors encountered across agents",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Aggregated list of recommendations from all agents",
    )
