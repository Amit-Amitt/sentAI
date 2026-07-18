import asyncio
import pytest

from sentinel_api.ai.agents.coordinator import CoordinatorAgent
from sentinel_api.ai.agents.coordinator.models import AgentStatus
from sentinel_api.ai.agents.coordinator.planner import IncidentPlanner
from sentinel_api.ai.agents.coordinator.scheduler import PlanScheduler
from sentinel_api.ai.agents.coordinator.validator import IncidentValidator
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)


@pytest.fixture
def mock_contexts():
    execution_context = ExecutionContext(
        request_id="req-coord-123",
        correlation_id="corr-coord-456",
        agent_id="test-coordinator",
    )
    incident_context = IncidentContext(
        incident_id="inc-coord-789",
        severity="SEV1",
        status="active",
        summary="Kubernetes ingress reporting 502 Bad Gateway alerts",
    )
    return incident_context, execution_context


def test_coordinator_validator(mock_contexts):
    incident, _ = mock_contexts
    validator = IncidentValidator()

    # Should validate successfully
    validator.validate(incident)

    # Empty summary failure
    invalid_incident = incident.copy(update={"summary": ""})
    with pytest.raises(AgentException) as exc:
        validator.validate(invalid_incident)
    assert "summary cannot be empty" in str(exc.value)

    # Missing incident_id failure
    invalid_incident = incident.copy(update={"incident_id": ""})
    with pytest.raises(AgentException) as exc:
        validator.validate(invalid_incident)
    assert "Incident ID is missing" in str(exc.value)


def test_coordinator_planner(mock_contexts):
    incident, _ = mock_contexts
    planner = IncidentPlanner()

    # 1. Test SEV1 plan
    plan_sev1 = planner.create_plan(incident)
    assert plan_sev1.items["Log Agent"].status == AgentStatus.PENDING
    assert plan_sev1.items["Metrics Agent"].status == AgentStatus.PENDING
    assert plan_sev1.items["Deployment Agent"].status == AgentStatus.PENDING
    assert plan_sev1.items["Review Agent"].status == AgentStatus.PENDING

    # 2. Test SEV3 plan (should skip Deployment and Review)
    low_sev_incident = incident.copy(update={"severity": "SEV3"})
    plan_sev3 = planner.create_plan(low_sev_incident)
    assert plan_sev3.items["Deployment Agent"].status == AgentStatus.SKIPPED
    assert plan_sev3.items["Review Agent"].status == AgentStatus.SKIPPED
    assert plan_sev3.items["Log Agent"].status == AgentStatus.PENDING

    # 3. Test skip_metrics flag in signals
    metrics_skipped_incident = incident.copy(
        update={"signals": {"skip_metrics": True}}
    )
    plan_skipped_metrics = planner.create_plan(metrics_skipped_incident)
    assert plan_skipped_metrics.items["Metrics Agent"].status == AgentStatus.SKIPPED


def test_coordinator_scheduler(mock_contexts):
    incident, _ = mock_contexts
    planner = IncidentPlanner()
    scheduler = PlanScheduler()

    # Get SEV1 plan and schedule it
    plan = planner.create_plan(incident)
    batches = scheduler.schedule(plan)

    # Verify that the topological sort grouped parallelizable agents
    # Batch 0: Log, Metrics, Deployment (independent nodes)
    # Batch 1: Review (depends on Deployment), Root Cause (depends on Log & Metrics)
    # Batch 2: Recommendation (depends on Root Cause)
    assert len(batches) >= 3
    assert "Log Agent" in batches[0]
    assert "Metrics Agent" in batches[0]
    assert "Deployment Agent" in batches[0]
    assert "Review Agent" in batches[1]
    assert "Root Cause Agent" in batches[1]
    assert "Recommendation Agent" in batches[2]

    # Verify cycle detection
    # Introduce dependency cycle: A -> B -> A
    plan.items["Log Agent"].dependencies = ["Recommendation Agent"]
    with pytest.raises(ValueError) as exc:
        scheduler.schedule(plan)
    assert "cyclic agent dependencies" in str(exc.value)


@pytest.mark.asyncio
async def test_coordinator_end_to_end(mock_contexts):
    incident, execution = mock_contexts
    coordinator = CoordinatorAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    # Set up some mock configs in input
    inputs = {
        "mock_behavior": {
            "Log Agent": {"confidence": 0.9},
            "Metrics Agent": {"confidence": 0.85},
            "Deployment Agent": {"confidence": 0.95},
            "Review Agent": {"confidence": 0.9},
            "Root Cause Agent": {"confidence": 0.88},
            "Recommendation Agent": {"confidence": 0.92},
        }
    }

    request = AgentRequest(
        execution_context=execution, incident_context=incident, inputs=inputs
    )

    result = await coordinator.execute(request, config)

    assert result.success is True
    # Output must be a dict representation of FinalExecutionState
    output = result.output
    assert "incident_summary" in output
    assert "execution_summary" in output
    assert "overall_confidence" in output
    assert output["overall_confidence"] > 0.8


@pytest.mark.asyncio
async def test_dispatcher_failure_policies(mock_contexts):
    incident, execution = mock_contexts
    coordinator = CoordinatorAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    # 1. SKIP Policy: Metric Agent fails but policy says skip
    inputs_skip = {
        "failure_policies": {"Metrics Agent": "SKIP"},
        "mock_behavior": {
            "Metrics Agent": {"fail_attempts": 3},  # fails (max retry=2)
            "Log Agent": {"confidence": 0.9},
            "Deployment Agent": {"confidence": 0.9},
            "Review Agent": {"confidence": 0.9},
            "Root Cause Agent": {"confidence": 0.9},
            "Recommendation Agent": {"confidence": 0.9},
        },
    }
    request = AgentRequest(
        execution_context=execution,
        incident_context=incident,
        inputs=inputs_skip,
    )
    result = await coordinator.execute(request, config)
    assert result.success is True
    assert "Metrics Agent" not in result.output["agent_results"]

    # 2. CONTINUE Policy: Metrics Agent fails but policy says continue
    inputs_continue = {
        "failure_policies": {"Metrics Agent": "CONTINUE"},
        "mock_behavior": {
            "Metrics Agent": {"fail_attempts": 3},  # fails (max retry=2)
            "Log Agent": {"confidence": 0.9},
            "Deployment Agent": {"confidence": 0.9},
            "Review Agent": {"confidence": 0.9},
            "Root Cause Agent": {"confidence": 0.9},
            "Recommendation Agent": {"confidence": 0.9},
        },
    }
    request = AgentRequest(
        execution_context=execution,
        incident_context=incident,
        inputs=inputs_continue,
    )
    result = await coordinator.execute(request, config)
    assert result.success is True
    assert "Metrics Agent" in result.output["agent_results"]
    assert result.output["agent_results"]["Metrics Agent"]["success"] is False

    # 3. ABORT Policy (Default): Metrics Agent fails and triggers execution abort
    inputs_abort = {
        "failure_policies": {"Metrics Agent": "ABORT"},
        "mock_behavior": {"Metrics Agent": {"fail_attempts": 3}},
    }
    request = AgentRequest(
        execution_context=execution,
        incident_context=incident,
        inputs=inputs_abort,
    )
    result = await coordinator.execute(request, config)
    # The agent execution itself catches the internal dispatch Exception and returns success=False
    assert result.success is False
    assert "Execution failed" in result.reasoning_summary


@pytest.mark.asyncio
async def test_dispatcher_timeout(mock_contexts):
    incident, execution = mock_contexts
    coordinator = CoordinatorAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    # Set Metrics Agent to simulate timeout
    inputs = {
        "failure_policies": {"Metrics Agent": "CONTINUE"},
        "mock_behavior": {"Metrics Agent": {"simulate_timeout": True}},
    }

    # Temporarily set plan timeout low for faster testing
    # We can override planner or configure dispatcher to simulate timeout
    # Our dispatcher reads plan_item.timeout, which is 15s. To make tests fast,
    # let's write mock behavior in inputs to simulate timeout immediately
    # inside _run_placeholder_agent
    request = AgentRequest(
        execution_context=execution, incident_context=incident, inputs=inputs
    )

    # Let's override planner creation during run or set plan item timeout manually.
    # In test_workflows we did similar checks. We can pass a timeout check or test it.
    # Let's verify timeout triggers correctly.
    # To keep the test fast, let's override planner or execute a manual dispatch test.
    from sentinel_api.ai.agents.coordinator.state_manager import StateManager
    plan = planner = IncidentPlanner().create_plan(incident)
    # Set timeout extremely small to trigger immediately
    plan.items["Metrics Agent"].timeout = 0.001
    
    state_manager = StateManager(plan)
    from sentinel_api.ai.agents.coordinator.dispatcher import AgentDispatcher
    dispatcher = AgentDispatcher(state_manager)

    # Simulate timeout execution
    behavior_inputs = {
        "failure_policies": {"Metrics Agent": "CONTINUE"},
        "mock_behavior": {"Metrics Agent": {"delay": 0.05}} # delay is larger than 0.001
    }
    
    res = await dispatcher.dispatch("Metrics Agent", incident, execution, behavior_inputs)
    assert res is not None
    assert res.success is False
    assert "TimeoutError" in res.output
