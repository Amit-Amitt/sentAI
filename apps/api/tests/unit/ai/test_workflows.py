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

@pytest.fixture(autouse=True)
def mock_agents(monkeypatch):
    async def mock_run(self, request, config):
        return {"summary": "mocked", "confidence": 0.9, "reasoning_summary": "mock reason", "metadata": {}}
    
    agents_to_mock = [
        "sentinel_api.ai.agents.log_agent.log_agent.LogAgent",
        "sentinel_api.ai.agents.metrics_agent.metrics_agent.MetricsAgent",
        "sentinel_api.ai.agents.deployment_agent.deployment_agent.DeploymentAgent",
        "sentinel_api.ai.agents.root_cause_agent.root_cause_agent.RootCauseAgent",
        "sentinel_api.ai.agents.recommendation_agent.recommendation_agent.RecommendationAgent",
        "sentinel_api.ai.agents.review_agent.review_agent.ReviewAgent",
    ]
    for agent_path in agents_to_mock:
        monkeypatch.setattr(f"{agent_path}._run", mock_run)


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

    from sentinel_api.ai.workflows.state import create_initial_state

    valid_state = create_initial_state(incident, execution)
    validate_workflow_state(valid_state)

    invalid_state = valid_state.copy()
    invalid_state.pop("status")
    with pytest.raises(WorkflowValidationError) as exc:
        validate_workflow_state(invalid_state)
    assert "Missing required state key: 'status'" in str(exc.value)


def test_graph_integrity_and_visualization():
    """Verifies static graph integrity checks and visualizer output."""
    visualizer = WorkflowVisualizer()

    mermaid_str = visualizer.generate_mermaid()
    assert "coordinator" in mermaid_str
    assert "log" in mermaid_str
    assert "metrics" in mermaid_str
    assert "deployment" in mermaid_str
    assert "merge_results" in mermaid_str
    assert "root_cause" in mermaid_str
    assert "similar_incidents" in mermaid_str
    assert "recommendation" in mermaid_str
    assert "report" in mermaid_str

    metadata = visualizer.get_visualization_metadata()
    assert "nodes" in metadata
    assert "edges" in metadata

    node_ids = {n["id"] for n in metadata["nodes"]}
    assert "coordinator" in node_ids
    assert "log" in node_ids
    assert "__start__" in node_ids
    assert "__end__" in node_ids


@pytest.mark.asyncio
async def test_sequential_workflow_execution(mock_contexts):
    """Tests the end-to-end default parallel/sequential workflow execution."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    result = await executor.start(incident, execution)

    assert result["status"] == "COMPLETED"
    assert result["duration_ms"] > 0
    assert "thread_id" in result

    state = result["state"]
    assert state["status"] == "COMPLETED"

    visited = state["visited_nodes"]
    
    assert "coordinator" in visited
    assert "log" in visited
    assert "metrics" in visited
    assert "deployment" in visited
    assert "merge_results" in visited
    assert "root_cause" in visited
    assert "similar_incidents" in visited
    assert "recommendation" in visited
    assert "report" in visited

    # 'log', 'metrics', 'deployment' must precede 'merge_results'
    idx_merge = visited.index("merge_results")
    assert visited.index("log") < idx_merge
    assert visited.index("metrics") < idx_merge
    assert visited.index("deployment") < idx_merge


@pytest.mark.asyncio
async def test_pause_and_resume_lifecycle(mock_contexts):
    """Tests pausing a workflow run and resuming from checkpoint."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Create an initial run and get thread_id
    result = await executor.start(incident, execution)
    thread_id = result["thread_id"]

    await executor.pause(thread_id)
    status_paused = await executor.get_status(thread_id)
    assert status_paused["status"] == "PAUSED"

    resume_res = await executor.resume(thread_id)
    assert resume_res["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_cancel_workflow_lifecycle(mock_contexts):
    """Tests cancelling a workflow run and ensuring it halts immediately."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    result = await executor.start(incident, execution)
    thread_id = result["thread_id"]

    cancel_res = await executor.cancel(thread_id)
    assert cancel_res["state"]["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_retry_and_failure_routing(mock_contexts):
    """Tests node failure simulation and retry routing."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    intermediates = {
        "fail_node": "log",
        "fail_node_max_retries": 2,
        "max_retries": 2,
    }

    result = await executor.start(
        incident, execution, intermediate_results=intermediates
    )

    assert result["status"] == "COMPLETED"
    state = result["state"]

    assert state["retry_count"].get("log") == 2
    assert len(state["errors"]) >= 2
    assert any(err["node"] == "log" for err in state["errors"])


@pytest.mark.asyncio
async def test_max_retries_exceeded_routing(mock_contexts):
    """Tests failure routing gracefully degrades when a node exceeds its maximum retry limit."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    intermediates = {
        "fail_node": "log",
        "fail_node_max_retries": 3,
        "max_retries": 1,
    }

    result = await executor.start(
        incident, execution, intermediate_results=intermediates
    )

    state = result["state"]
    # Should still complete because we gracefully degrade to 'merge_results' in router
    assert state["status"] == "COMPLETED"
    assert state["retry_count"].get("log") == 2


@pytest.mark.asyncio
async def test_timeout_handling(mock_contexts):
    """Tests executor timeout capabilities."""
    incident, execution = mock_contexts
    executor = WorkflowExecutor()

    # Run with a very low timeout
    result = await executor.start(incident, execution, timeout=0.00001)

    assert result["status"] == "FAILED"
    assert "error" in result
    assert "TimeoutError" in result["error"] or "timeout" in result["error"].lower()
