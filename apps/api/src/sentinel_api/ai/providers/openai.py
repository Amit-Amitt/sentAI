from openai import AsyncOpenAI
from pydantic import BaseModel

from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import ProviderException
from sentinel_api.ai.providers.base import BaseProvider
from sentinel_api.config.settings import settings


class OpenAIProvider(BaseProvider):
    """OpenAI implementation of the BaseProvider contract."""

    def __init__(self) -> None:
        api_key = settings.OPENAI_API_KEY or "mock-openai-key"
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str, config: ModelConfig) -> str:
        """Sends an async chat completion request to OpenAI and returns raw text."""
        try:
            response = await self.client.chat.completions.create(
                model=config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
            )
            content = response.choices[0].message.content
            if content is None:
                raise ProviderException("OpenAI API returned an empty completion.")
            return content
        except Exception as e:
            raise ProviderException(f"OpenAI text generation failed: {e}") from e

    async def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
        config: ModelConfig,
    ) -> BaseModel:
        """Sends an async completion request and parses it into a Pydantic model."""
        try:
            response = await self.client.beta.chat.completions.parse(
                model=config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout,
                response_format=response_model,
            )
            parsed = response.choices[0].message.parsed
            if parsed is None:
                raise ProviderException(
                    "OpenAI failed to parse the response into the requested schema."
                )
            return parsed
        except Exception as e:
            raise ProviderException(f"OpenAI structured generation failed: {e}") from e
