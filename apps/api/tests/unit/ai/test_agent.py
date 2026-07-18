from typing import Any
from unittest.mock import AsyncMock

import pytest

from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)


class MockAgent(BaseAgent):
    """Concrete mock implementation of BaseAgent for testing execution lifecycle."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.mock_run_func = AsyncMock()

    def validate(self, request: AgentRequest) -> None:
        super().validate(request)
        if "forbidden" in request.inputs:
            raise AgentException("Forbidden input detected")

    def confidence(self, output: Any) -> float:
        if isinstance(output, dict) and "custom_conf" in output:
            return output["custom_conf"]
        return super().confidence(output)

    async def _run(self, request: AgentRequest, config: ModelConfig) -> Any:
        return await self.mock_run_func(request, config)


@pytest.fixture
def agent_request() -> AgentRequest:
    return AgentRequest(
        execution_context=ExecutionContext(
            request_id="req-abc",
            correlation_id="corr-xyz",
            agent_id="mock-agent-1",
        ),
        incident_context=IncidentContext(
            incident_id="inc-123",
            severity="SEV1",
            status="active",
            summary="Disk space critical warning",
        ),
        inputs={"param": "value"},
    )


@pytest.mark.asyncio
async def test_agent_execute_success(agent_request):
    agent = MockAgent("MockTestAgent")
    config = ModelConfig(provider="openai", model_name="gpt-4")

    agent.mock_run_func.return_value = {
        "reasoning_summary": "Disk cleanup executed",
        "custom_conf": 0.99,
    }

    result = await agent.execute(agent_request, config)

    assert result.success is True
    assert result.confidence == 0.99
    assert result.reasoning_summary == "Disk cleanup executed"
    assert result.processing_time_ms > 0
    assert result.metadata["agent_name"] == "MockTestAgent"


@pytest.mark.asyncio
async def test_agent_execute_validation_failure(agent_request):
    agent = MockAgent("MockTestAgent")
    config = ModelConfig(provider="openai", model_name="gpt-4")

    agent_request.inputs["forbidden"] = True
    result = await agent.execute(agent_request, config)

    assert result.success is False
    assert "Forbidden input detected" in result.reasoning_summary
    assert result.confidence == 0.0


@pytest.mark.asyncio
async def test_agent_retry_strategy(agent_request):
    agent = MockAgent("MockTestAgent")
    config = ModelConfig(provider="openai", model_name="gpt-4")

    # Fail twice, then succeed
    attempts = 0

    async def mock_runner(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Transient error")
        return {"reasoning_summary": "Success after retries"}

    agent.mock_run_func.side_effect = mock_runner
    result = await agent.execute(agent_request, config)

    assert result.success is True
    assert attempts == 3
    assert result.reasoning_summary == "Success after retries"
