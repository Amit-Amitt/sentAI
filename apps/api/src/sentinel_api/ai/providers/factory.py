from typing import ClassVar

from sentinel_api.ai.exceptions import ProviderException
from sentinel_api.ai.providers.base import BaseProvider
from sentinel_api.ai.providers.gemini import GeminiProvider
from sentinel_api.ai.providers.openai import OpenAIProvider


class ProviderFactory:
    """Factory to dynamically instantiate and retrieve cached LLM providers."""

    _instances: ClassVar[dict[str, BaseProvider]] = {}

    @classmethod
    def get_provider(cls, name: str) -> BaseProvider:
        """Retrieves or instantiates the requested LLM provider."""
        provider_key = name.lower().strip()
        if provider_key not in cls._instances:
            if provider_key == "openai":
                cls._instances[provider_key] = OpenAIProvider()
            elif provider_key == "gemini":
                cls._instances[provider_key] = GeminiProvider()
            else:
                raise ProviderException(
                    f"Unsupported LLM provider: '{name}'. "
                    "Supported providers: 'openai', 'gemini'."
                )
        return cls._instances[provider_key]
