from abc import ABC, abstractmethod
from typing import Any, Literal


class BaseMemory(ABC):
    """Abstract interface defining the memory access contract for agents."""

    @abstractmethod
    async def store(
        self,
        key: str,
        value: Any,
        memory_type: Literal["short_term", "long_term", "vector"] = "short_term",
    ) -> None:
        """Stores a value in the specified memory type partition."""
        pass

    @abstractmethod
    async def retrieve(
        self,
        key: str,
        memory_type: Literal["short_term", "long_term", "vector"] = "short_term",
    ) -> Any:
        """Retrieves a value from the specified memory type partition."""
        pass

    @abstractmethod
    async def clear(
        self,
        memory_type: Literal["short_term", "long_term", "vector"] = "short_term",
    ) -> None:
        """Clears all stored states for the specified memory type partition."""
        pass
