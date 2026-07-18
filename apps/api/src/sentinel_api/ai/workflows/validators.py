from typing import Any
from sentinel_api.ai.workflows.state import WorkflowState
from sentinel_api.ai.schemas.models import IncidentContext, ExecutionContext


class WorkflowValidationError(Exception):
    """Exception raised when workflow validation fails."""
    pass


def validate_workflow_state(state: Any) -> None:
    """Validates that a workflow state dict conforms to the WorkflowState definition.

    Raises:
        WorkflowValidationError: If any validation rule is violated.
    """
    if not isinstance(state, dict):
        raise WorkflowValidationError("Workflow state must be a dictionary.")

    required_keys = [
        "incident",
        "execution_context",
        "current_node",
        "visited_nodes",
        "intermediate_results",
        "agent_outputs",
        "confidence_scores",
        "execution_timeline",
        "errors",
        "retry_count",
        "status",
    ]

    for key in required_keys:
        if key not in state:
            raise WorkflowValidationError(f"Missing required state key: '{key}'")

    # Type validate incident
    if not isinstance(state["incident"], IncidentContext):
        raise WorkflowValidationError(
            f"State field 'incident' must be IncidentContext, got {type(state['incident'])}"
        )

    # Type validate execution_context
    if not isinstance(state["execution_context"], ExecutionContext):
        raise WorkflowValidationError(
            f"State field 'execution_context' must be ExecutionContext, got {type(state['execution_context'])}"
        )

    # Validate lists and dicts
    if not isinstance(state["visited_nodes"], list):
        raise WorkflowValidationError("State field 'visited_nodes' must be a list of strings.")

    if not isinstance(state["intermediate_results"], dict):
        raise WorkflowValidationError("State field 'intermediate_results' must be a dictionary.")

    if not isinstance(state["agent_outputs"], dict):
        raise WorkflowValidationError("State field 'agent_outputs' must be a dictionary.")

    if not isinstance(state["confidence_scores"], dict):
        raise WorkflowValidationError("State field 'confidence_scores' must be a dictionary.")

    if not isinstance(state["execution_timeline"], list):
        raise WorkflowValidationError("State field 'execution_timeline' must be a list of timeline events.")

    if not isinstance(state["errors"], list):
        raise WorkflowValidationError("State field 'errors' must be a list of errors.")

    if not isinstance(state["retry_count"], dict):
        raise WorkflowValidationError("State field 'retry_count' must be a dictionary.")

    if not isinstance(state["status"], str):
        raise WorkflowValidationError("State field 'status' must be a string.")


def validate_transition(from_node: str, to_node: str, valid_transitions: dict[str, list[str]]) -> None:
    """Validates that a transition between two nodes is registered in the graph topology.

    Raises:
        WorkflowValidationError: If the transition is illegal.
    """
    if from_node not in valid_transitions:
        raise WorkflowValidationError(f"Source node '{from_node}' is not registered in graph topology.")

    allowed = valid_transitions[from_node]
    if to_node not in allowed:
        raise WorkflowValidationError(
            f"Illegal transition from '{from_node}' to '{to_node}'. Allowed targets: {allowed}"
        )


def validate_graph_integrity(
    adjacency_list: dict[str, list[str]],
    entry_point: str,
    exit_points: list[str]
) -> None:
    """Performs static analysis to verify the structural integrity of the graph topology.

    Raises:
        WorkflowValidationError: If there are disconnected components or missing entry/exit nodes.
    """
    if not entry_point:
        raise WorkflowValidationError("Graph has no valid entry point.")

    if entry_point not in adjacency_list:
        raise WorkflowValidationError(f"Entry point '{entry_point}' is not in the graph nodes.")

    if not exit_points:
        raise WorkflowValidationError("Graph must have at least one exit point.")

    # Run a simple BFS/DFS from the entry point to ensure reachability of all nodes
    visited = set()
    queue = [entry_point]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        for neighbor in adjacency_list.get(current, []):
            if neighbor not in visited and neighbor != "__end__":
                queue.append(neighbor)

    all_nodes = set(adjacency_list.keys())
    # Allow target nodes in adjacency list values that might not have outgoing edges (i.e. leaf nodes or __end__)
    all_targets = {t for targets in adjacency_list.values() for t in targets if t != "__end__"}
    expected_nodes = all_nodes.union(all_targets)

    unreachable = expected_nodes - visited
    if unreachable:
        raise WorkflowValidationError(f"Disconnected components detected. Unreachable nodes: {unreachable}")

    # Ensure all exit points are reachable from the entry point
    for exit_node in exit_points:
        if exit_node != "__end__" and exit_node not in visited:
            raise WorkflowValidationError(f"Exit point '{exit_node}' is unreachable from entry point '{entry_point}'.")
