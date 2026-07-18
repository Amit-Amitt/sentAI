import google.generativeai as genai
from pydantic import BaseModel

from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import ProviderException
from sentinel_api.ai.providers.base import BaseProvider
from sentinel_api.config.settings import settings


class GeminiProvider(BaseProvider):
    """Google Gemini implementation of the BaseProvider contract."""

    def __init__(self) -> None:
        api_key = settings.GEMINI_API_KEY or "mock-gemini-key"
        genai.configure(api_key=api_key)

    async def generate(self, prompt: str, config: ModelConfig) -> str:
        """Sends an async generation request to Gemini and returns raw text."""
        try:
            model = genai.GenerativeModel(config.model_name)
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config.temperature,
                    max_output_tokens=config.max_tokens,
                ),
            )
            return response.text
        except Exception as e:
            raise ProviderException(f"Gemini text generation failed: {e}") from e

    async def generate_structured(
        self,
        prompt: str,
        response_model: type[BaseModel],
        config: ModelConfig,
    ) -> BaseModel:
        """Sends an async structured completion request and parses it into a Pydantic model."""
        try:
            model = genai.GenerativeModel(config.model_name)
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=config.temperature,
                    max_output_tokens=config.max_tokens,
                    response_mime_type="application/json",
                    response_schema=response_model,
                ),
            )
            text = response.text
            return response_model.model_validate_json(text)
        except Exception as e:
            raise ProviderException(f"Gemini structured generation failed: {e}") from e
