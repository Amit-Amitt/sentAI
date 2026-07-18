from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel

from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import ProviderException
from sentinel_api.ai.providers import GeminiProvider, OpenAIProvider, ProviderFactory


class MockResponseModel(BaseModel):
    key: str
    val: int


@pytest.mark.asyncio
async def test_provider_factory_resolution():
    openai_prov = ProviderFactory.get_provider("openai")
    assert isinstance(openai_prov, OpenAIProvider)

    gemini_prov = ProviderFactory.get_provider("gemini")
    assert isinstance(gemini_prov, GeminiProvider)

    # Test cache reuse
    assert ProviderFactory.get_provider("openai") is openai_prov

    with pytest.raises(ProviderException):
        ProviderFactory.get_provider("unsupported")


@pytest.mark.asyncio
@patch("sentinel_api.ai.providers.openai.AsyncOpenAI")
async def test_openai_provider_generation(mock_openai_class):
    mock_client = mock_openai_class.return_value
    mock_completions = mock_client.chat.completions.create = AsyncMock()

    mock_choice = AsyncMock()
    mock_choice.message.content = "Hello from OpenAI"
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    mock_completions.return_value = mock_response

    openai_prov = OpenAIProvider()
    config = ModelConfig(provider="openai", model_name="gpt-4")
    result = await openai_prov.generate("test prompt", config)

    assert result == "Hello from OpenAI"
    mock_completions.assert_called_once()


@pytest.mark.asyncio
@patch("sentinel_api.ai.providers.openai.AsyncOpenAI")
async def test_openai_provider_structured(mock_openai_class):
    mock_client = mock_openai_class.return_value
    mock_parse = mock_client.beta.chat.completions.parse = AsyncMock()

    mock_choice = AsyncMock()
    mock_choice.message.parsed = MockResponseModel(key="abc", val=123)
    mock_response = AsyncMock()
    mock_response.choices = [mock_choice]
    mock_parse.return_value = mock_response

    openai_prov = OpenAIProvider()
    config = ModelConfig(provider="openai", model_name="gpt-4")
    result = await openai_prov.generate_structured(
        "test prompt", MockResponseModel, config
    )

    assert isinstance(result, MockResponseModel)
    assert result.key == "abc"
    assert result.val == 123
