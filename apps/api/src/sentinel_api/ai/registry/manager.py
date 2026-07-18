from typing import Any, ClassVar

from sentinel_api.ai.exceptions import RegistryException
from sentinel_api.ai.runtime.agent import BaseAgent


class AgentRegistry:
    """Dynamic registry for cataloging and instantiating Sentinel AI agents."""

    _registry: ClassVar[dict[str, type[BaseAgent]]] = {}
    _instances: ClassVar[dict[str, BaseAgent]] = {}

    @classmethod
    def register(cls, name: str, agent_class: type[BaseAgent]) -> None:
        """Registers a BaseAgent class mapping it to a key string."""
        clean_name = name.strip()
        if not clean_name:
            raise RegistryException("Cannot register agent with empty name.")
        cls._registry[clean_name] = agent_class

    @classmethod
    def get_agent(cls, agent_name: str, *args: Any, **kwargs: Any) -> BaseAgent:
        """Retrieves or instantiates a registered agent class name."""
        clean_name = agent_name.strip()
        if clean_name not in cls._registry:
            raise RegistryException(
                f"Agent '{agent_name}' is not registered "
                "in the system registry."
            )

        if clean_name not in cls._instances:
            try:
                # Instantiate and cache agent instance
                cls._instances[clean_name] = cls._registry[clean_name](*args, **kwargs)
            except Exception as e:
                raise RegistryException(
                    f"Failed to instantiate registered agent '{agent_name}': {e}"
                ) from e

        return cls._instances[clean_name]

    @classmethod
    def list_agents(cls) -> list[str]:
        """Lists all registered agent keys."""
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        """Clears the registry catalog and instantiated cache."""
        cls._registry.clear()
        cls._instances.clear()
