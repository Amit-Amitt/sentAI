from typing import Literal

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration options for dynamic LLM requests."""

    provider: Literal["openai", "gemini"] = Field(
        default="openai",
        description="The target LLM provider (e.g. openai, gemini)",
    )
    model_name: str = Field(
        default="gpt-4-turbo",
        description="Specific model identifier (e.g. gpt-4-turbo, gemini-1.5-pro)",
    )
    temperature: float = Field(
        default=0.0,
        description="Controls model creativity / randomness. Standard default is 0.0 for incidents.",
    )
    max_tokens: int = Field(
        default=4096,
        description="Maximum tokens allowed in the response generation.",
    )
    timeout: float = Field(
        default=30.0,
        description="Timeout threshold for provider API requests.",
    )
