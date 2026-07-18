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

    incident: IncidentContext
    execution_context: ExecutionContext
    current_node: Annotated[str, last_value_reducer]
    visited_nodes: Annotated[list[str], append_reducer]
    intermediate_results: Annotated[dict[str, Any], dict_merge_reducer]
    agent_outputs: Annotated[dict[str, AgentResult], dict_merge_reducer]
    confidence_scores: Annotated[dict[str, float], dict_merge_reducer]
    execution_timeline: Annotated[list[dict[str, Any]], append_reducer]
    errors: Annotated[list[dict[str, Any]], append_reducer]
    retry_count: Annotated[dict[str, int], dict_merge_reducer]
    status: Annotated[str, last_value_reducer]  # e.g., "RUNNING", "PAUSED", "COMPLETED", "FAILED", "CANCELLED"


def create_initial_state(
    incident: IncidentContext,
    execution_context: ExecutionContext,
) -> WorkflowState:
    """Helper function to initialize a new WorkflowState with default values."""
    return {
        "incident": incident,
        "execution_context": execution_context,
        "current_node": "",
        "visited_nodes": [],
        "intermediate_results": {},
        "agent_outputs": {},
        "confidence_scores": {},
        "execution_timeline": [],
        "errors": [],
        "retry_count": {},
        "status": "RUNNING",
    }
