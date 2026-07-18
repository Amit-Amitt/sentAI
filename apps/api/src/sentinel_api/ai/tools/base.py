from abc import ABC, abstractmethod

from pydantic import BaseModel

from sentinel_api.ai.schemas.models import ToolResult


class BaseTool(ABC):
    """Abstract base class for tools that agents can execute."""

    name: str
    description: str
    args_schema: type[BaseModel]

    @abstractmethod
    async def run(self, **kwargs) -> ToolResult:
        """Asynchronously executes the tool with input arguments."""
        pass
