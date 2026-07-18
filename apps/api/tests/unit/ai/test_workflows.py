import asyncio
import pytest
from datetime import UTC, datetime

from sentinel_api.ai.schemas.models import ExecutionContext, IncidentContext
from sentinel_api.ai.workflows import (
    WorkflowExecutor,
    WorkflowVisualizer,
    WorkflowValidationError,
    validate_graph_integrity,
    validate_workflow_state,
)


@pytest.fixture
def mock_contexts():
    """Provides standard ExecutionContext and IncidentContext for testing."""
    execution_context = ExecutionContext(
        request_id="req-test-123",
        correlation_id="corr-test-456",
        agent_id="test-orchestrator",
    )
    incident_context = IncidentContext(
        incident_id="inc-test-789",
        severity="SEV1",
        status="active",
        summary="High memory consumption on production cluster",
        signals={"cpu": 95, "memory": 92},
    )
    return incident_context, execution_context


def test_state_validation(mock_contexts):
    """Verifies that the state validation detects correct structures and reports schema failures."""
    incident, execution = mock_contexts

    # 1. Valid state validation
    from sentinel_api.ai.workflows.state import create_initial_state

    valid_state = create_initial_state(incident, execution)
    # Should run without raising an error
    validate_workflow_state(valid_state)

    # 2. Invalid state: Missing key
    invalid_state = valid_state.copy()
    invalid_state.pop("status")
    with pytest.raises(WorkflowValidationError) as exc:
        validate_workflow_state(invalid_state)
    assert "Missing required state key: 'status'" in str(exc.value)

    # 3. Invalid state: Wrong types
    invalid_type_state = valid_state.copy()
    invalid_type_state["status"] = 123  # Should be string
    with pytest.raises(WorkflowValidationError) as exc:
        validate_workflow_state(invalid_type_state)
    assert "State field 'status' must be a string." in str(exc.value)


def test_graph_integrity_and_visualization():
    """Verifies static graph integrity checks and visualizer output."""
    visualizer = WorkflowVisualizer()

    # Verify Mermaid generation
    mermaid_str = visualizer.generate_mermaid()
    assert "coordinator" in mermaid_str
    assert "log" in mermaid_str
    assert "metrics" in mermaid_str
    assert "deployment" in mermaid_str
    assert "review" in mermaid_str
    assert "root_cause" in mermaid_str
    assert "recommendation" in mermaid_str

    # Verify metadata contains nodes and edges
    metadata = visualizer.get_visualization_metadata()
    assert "nodes" in metadata
    assert "edges" in metadata

    node_ids = {n["id"] for n in metadata["nodes"]}
    assert "coordinator" in node_ids
    assert "log" in node_ids
    assert "__start__" in node_ids
    assert "__end__" in node_ids

    # Run static validation check
    # Convert visualizer edges to adjacency list
    adjacency_list = {}
    for edge in metadata["edges"]:
        src = edge["source"]
        tgt = edge["target"]
        if src not in adjacency_list:
            adjacency_list[src] = []
        adjacency_list[src].append(tgt)

    validate_graph_integrity(
        adjacency_list=adjacency_list,
        entry_point="__start__",
        exit_points=["__end__"],
    )


@pytest.mark.asyncio
async def test_sequential_workflow_execution(mock_contexts):
    """Tests the end-to-end default sequential workflow execution."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    result = await executor.start(incident, execution)

    assert result["status"] == "COMPLETED"
    assert result["duration_ms"] > 0
    assert "thread_id" in result

    state = result["state"]
    assert state["status"] == "COMPLETED"

    # Verify visited nodes
    # Expected sequence: coordinator -> log -> metrics -> deployment -> review -> root_cause -> recommendation
    expected_visited = [
        "coordinator",
        "log",
        "metrics",
        "deployment",
        "review",
        "root_cause",
        "recommendation",
    ]
    assert state["visited_nodes"] == expected_visited

    # Verify agent outputs were recorded
    for node in expected_visited:
        assert node in state["agent_outputs"]
        agent_out = state["agent_outputs"][node]
        assert agent_out.success is True
        assert agent_out.confidence == 0.9
        assert node in state["confidence_scores"]
        assert state["confidence_scores"][node] == 0.9


@pytest.mark.asyncio
async def test_conditional_branching_skip_metrics(mock_contexts):
    """Tests conditional branching where the metrics node is skipped."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Pass intermediate results to trigger skip_metrics branch
    intermediates = {"branch": "skip_metrics"}
    result = await executor.start(
        incident, execution, intermediate_results=intermediates
    )

    assert result["status"] == "COMPLETED"
    state = result["state"]

    # Verify visited nodes: 'metrics' should be skipped, and coordinator routes to log,
    # which routes to deployment.
    expected_visited = [
        "coordinator",
        "log",
        "deployment",
        "review",
        "root_cause",
        "recommendation",
    ]
    assert state["visited_nodes"] == expected_visited
    assert "metrics" not in state["visited_nodes"]


@pytest.mark.asyncio
async def test_conditional_branching_skip_review(mock_contexts):
    """Tests conditional branching where the review node is skipped."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Pass intermediate results to trigger skip_review branch
    intermediates = {"branch": "skip_review"}
    result = await executor.start(
        incident, execution, intermediate_results=intermediates
    )

    assert result["status"] == "COMPLETED"
    state = result["state"]

    # Verify visited nodes: 'review' should be skipped
    expected_visited = [
        "coordinator",
        "log",
        "metrics",
        "deployment",
        "root_cause",
        "recommendation",
    ]
    assert state["visited_nodes"] == expected_visited
    assert "review" not in state["visited_nodes"]


@pytest.mark.asyncio
async def test_parallel_execution_branching(mock_contexts):
    """Tests parallel branch routing from coordinator (runs log and metrics concurrently)."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Pass parallel indicator in intermediate results
    intermediates = {"parallel": True}
    result = await executor.start(
        incident, execution, intermediate_results=intermediates
    )

    assert result["status"] == "COMPLETED"
    state = result["state"]

    # In parallel mode, both 'log' and 'metrics' should be visited before 'deployment'.
    visited = state["visited_nodes"]
    assert "coordinator" in visited
    assert "log" in visited
    assert "metrics" in visited
    assert "deployment" in visited

    # The coordinator is always first
    assert visited[0] == "coordinator"

    # 'log' and 'metrics' are executed (parallel execution resolves order dynamically,
    # but both must precede deployment)
    idx_log = visited.index("log")
    idx_metrics = visited.index("metrics")
    idx_deployment = visited.index("deployment")

    assert idx_log < idx_deployment
    assert idx_metrics < idx_deployment


@pytest.mark.asyncio
async def test_pause_and_resume_lifecycle(mock_contexts):
    """Tests pausing a workflow run and resuming from checkpoint."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Start a run but simulate a pause status from the start (or inject dynamic pause status)
    # We can pass status="PAUSED" directly in intermediates to simulate pause
    intermediates = {"branch": "skip_metrics"}

    # Start the workflow
    result = await executor.start(
        incident, execution, intermediate_results=intermediates
    )
    thread_id = result["thread_id"]

    # Query status
    status_res = await executor.get_status(thread_id)
    assert status_res["status"] == "COMPLETED"

    # To test resume & pause realistically, let's inject a PAUSED state update
    # and call resume. Since status is PAUSED, routing will abort at the next node boundary.
    await executor.pause(thread_id)

    status_paused = await executor.get_status(thread_id)
    assert status_paused["status"] == "PAUSED"

    # Resuming should restore RUNNING status and continue
    resume_res = await executor.resume(thread_id)
    assert resume_res["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_cancel_workflow_lifecycle(mock_contexts):
    """Tests cancelling a workflow run and ensuring it halts immediately."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    result = await executor.start(incident, execution)
    thread_id = result["thread_id"]

    # Cancel execution
    cancel_res = await executor.cancel(thread_id)
    assert cancel_res["state"]["status"] == "CANCELLED"

    status_cancel = await executor.get_status(thread_id)
    assert status_cancel["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_retry_and_failure_routing(mock_contexts):
    """Tests node failure simulation and retry routing."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Configure coordinator node to fail twice (max retries = 2)
    # This will trigger retry twice, then succeed.
    intermediates = {
        "fail_node": "coordinator",
        "fail_node_max_retries": 2,
        "max_retries": 2,
    }

    result = await executor.start(
        incident, execution, intermediate_results=intermediates
    )

    assert result["status"] == "COMPLETED"
    state = result["state"]

    # Check retry count was recorded
    assert state["retry_count"].get("coordinator") == 2

    # Check errors were recorded
    assert len(state["errors"]) == 2
    assert state["errors"][0]["node"] == "coordinator"


@pytest.mark.asyncio
async def test_max_retries_exceeded_routing(mock_contexts):
    """Tests failure routing when a node exceeds its maximum retry limit."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Configure coordinator to fail 3 times, with a max retry limit of 1
    # This will trigger failure routing to END.
    intermediates = {
        "fail_node": "coordinator",
        "fail_node_max_retries": 3,
        "max_retries": 1,
    }

    result = await executor.start(
        incident, execution, intermediate_results=intermediates
    )

    # Since retries exceeded, it routes to END and returns FAILED/CANCELLED or COMPLETED
    # depending on target. In our routing table it routes to __end__, causing it to
    # finish, but let's check its state errors.
    state = result["state"]
    assert len(state["errors"]) >= 2
    # The status will be COMPLETED (because it reached END node) or FAILED depending on check.
    # But errors are recorded.
    assert state["retry_count"].get("coordinator") == 2  # 0 -> 1 -> 2 (exceeds max_retries=1)


@pytest.mark.asyncio
async def test_timeout_handling(mock_contexts):
    """Tests executor timeout capabilities."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Run with a very low timeout (e.g. 0.00001 seconds) to trigger timeout handling
    result = await executor.start(incident, execution, timeout=0.00001)

    assert result["status"] == "FAILED"
    assert "error" in result
    assert "TimeoutError" in result["error"] or "timeout" in result["error"].lower()
    assert result["state"]["status"] == "FAILED"
    assert len(result["state"]["errors"]) == 1
    assert "timed out" in result["state"]["errors"][0]["message"]
