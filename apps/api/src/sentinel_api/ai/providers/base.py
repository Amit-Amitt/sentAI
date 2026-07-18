from abc import ABC, abstractmethod

from pydantic import BaseModel

from sentinel_api.ai.config import ModelConfig


class BaseProvider(ABC):
    """Abstract base class establishing the contract for all LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, config: ModelConfig) -> str:
        """Asynchronously requests text completion from the LLM provider."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
        config: ModelConfig,
    ) -> BaseModel:
        """Asynchronously requests structured Pydantic completion from the LLM provider."""
        pass
