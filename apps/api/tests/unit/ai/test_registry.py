from typing import Any

import pytest

from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import RegistryException
from sentinel_api.ai.registry import AgentRegistry
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import AgentRequest


class DummyAgent(BaseAgent):
    """Simple concrete agent subclass to test registry bindings."""

    async def _run(self, request: AgentRequest, config: ModelConfig) -> Any:
        return "dummy_result"


def test_registry_lifecycle():
    # Clean setup
    AgentRegistry.clear()

    # Register class mapping
    AgentRegistry.register("dummy_agent", DummyAgent)
    assert "dummy_agent" in AgentRegistry.list_agents()

    # Retrieve instanced agent
    agent_instance = AgentRegistry.get_agent("dummy_agent", name="DummyTester")
    assert isinstance(agent_instance, DummyAgent)
    assert agent_instance.name == "DummyTester"

    # Verify cached singleton instantiation
    assert AgentRegistry.get_agent("dummy_agent") is agent_instance

    # Assert unregistered lookup error
    with pytest.raises(RegistryException):
        AgentRegistry.get_agent("unknown_agent")

    # Assert empty string registration error
    with pytest.raises(RegistryException):
        AgentRegistry.register("  ", DummyAgent)

    # Clear and check
    AgentRegistry.clear()
    assert len(AgentRegistry.list_agents()) == 0
