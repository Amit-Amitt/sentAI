from typing import Annotated, Any
from typing_extensions import TypedDict

from sentinel_api.ai.schemas.models import ExecutionContext, IncidentContext, AgentResult


def append_reducer(left: list[Any] | None, right: list[Any] | Any | None) -> list[Any]:
    """Helper reducer that appends incoming items to a list in LangGraph state updates."""
    if left is None:
        left = []
    if right is None:
        return left
    if isinstance(right, list):
        return left + right
    return left + [right]


def dict_merge_reducer(
    left: dict[str, Any] | None, right: dict[str, Any] | None
) -> dict[str, Any]:
    """Helper reducer that merges dictionary updates in LangGraph, enabling concurrent updates from parallel executing nodes."""
    if left is None:
        left = {}
    if right is None:
        return left
    # Merge dictionaries, overriding left keys with right keys
    return {**left, **right}


def last_value_reducer(left: Any, right: Any) -> Any:
    """Helper reducer that resolves concurrent writes by keeping the last value."""
    return right


class WorkflowState(TypedDict):
    """Strongly typed shared workflow state for Sentinel AI's LangGraph orchestrator."""

    # Requested Fields
    incident_id: Annotated[str, last_value_reducer]
    incident_title: Annotated[str, last_value_reducer]
    incident_severity: Annotated[str, last_value_reducer]
    incident_timestamp: Annotated[str, last_value_reducer]
    
    logs: Annotated[list[dict[str, Any]], append_reducer]
    metrics: Annotated[list[dict[str, Any]], append_reducer]
    deployment_events: Annotated[list[dict[str, Any]], append_reducer]
    alerts: Annotated[list[dict[str, Any]], append_reducer]
    
    ai_memory: Annotated[dict[str, Any], dict_merge_reducer]
    similar_incidents: Annotated[list[dict[str, Any]], append_reducer]
    
    log_analysis: Annotated[dict[str, Any], dict_merge_reducer]
    metrics_analysis: Annotated[dict[str, Any], dict_merge_reducer]
    deployment_analysis: Annotated[dict[str, Any], dict_merge_reducer]
    root_cause: Annotated[dict[str, Any], dict_merge_reducer]
    
    confidence_score: Annotated[float, last_value_reducer]
    recommended_actions: Annotated[list[dict[str, Any]], append_reducer]
    incident_timeline: Annotated[list[dict[str, Any]], append_reducer]
    generated_report: Annotated[dict[str, Any], dict_merge_reducer]
    github_patch: Annotated[dict[str, Any], dict_merge_reducer]
    execution_history: Annotated[list[dict[str, Any]], append_reducer]
    execution_timeline: Annotated[list[dict[str, Any]], append_reducer]
    agent_status: Annotated[dict[str, str], dict_merge_reducer]

    # Required Operational Context
    incident: IncidentContext
    execution_context: ExecutionContext
    current_node: Annotated[str, last_value_reducer]
    visited_nodes: Annotated[list[str], append_reducer]
    intermediate_results: Annotated[dict[str, Any], dict_merge_reducer]
    agent_outputs: Annotated[dict[str, AgentResult], dict_merge_reducer]
    confidence_scores: Annotated[dict[str, float], dict_merge_reducer]
    errors: Annotated[list[dict[str, Any]], append_reducer]
    retry_count: Annotated[dict[str, int], dict_merge_reducer]
    status: Annotated[str, last_value_reducer]  # RUNNING, PAUSED, COMPLETED, FAILED, CANCELLED


def create_initial_state(
    incident: IncidentContext,
    execution_context: ExecutionContext,
) -> WorkflowState:
    """Helper function to initialize a new WorkflowState with default values."""
    return {
        "incident_id": incident.incident_id,
        "incident_title": incident.summary,
        "incident_severity": incident.severity,
        "incident_timestamp": incident.signals.get("timestamp", ""),
        "logs": [],
        "metrics": [],
        "deployment_events": [],
        "alerts": [],
        "ai_memory": {},
        "similar_incidents": [],
        "log_analysis": {},
        "metrics_analysis": {},
        "deployment_analysis": {},
        "root_cause": {},
        "confidence_score": 0.0,
        "recommended_actions": [],
        "incident_timeline": [],
        "generated_report": {},
        "github_patch": {},
        "execution_history": [],
        "execution_timeline": [],
        "agent_status": {},
        "incident": incident,
        "execution_context": execution_context,
        "current_node": "",
        "visited_nodes": [],
        "intermediate_results": {},
        "agent_outputs": {},
        "confidence_scores": {},
        "errors": [],
        "retry_count": {},
        "status": "RUNNING",
    }
