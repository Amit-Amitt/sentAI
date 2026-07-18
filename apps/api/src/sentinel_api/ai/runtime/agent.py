import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import structlog

from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.schemas.models import AgentRequest, AgentResult


class BaseAgent(ABC):
    """Abstract base class that all operational Sentinel AI agents must inherit from."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = structlog.get_logger(f"sentinel_api.ai.agents.{name}")

    def validate(self, request: AgentRequest) -> None:
        """Validates inputs of the incoming request. Subclasses should override this."""
        if not request.execution_context.request_id:
            raise AgentException("Request ID is missing in execution context.")
        if not request.execution_context.agent_id:
            raise AgentException("Agent ID is missing in execution context.")

    def confidence(self, output: Any) -> float:
        """Extracts or calculates confidence score from agent output findings. Defaults to 0.8."""
        if isinstance(output, dict) and "confidence" in output:
            try:
                return float(output["confidence"])
            except (TypeError, ValueError):
                pass
        return 0.8

    async def retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        retries: int = 3,
        backoff_factor: float = 2.0,
        initial_delay: float = 1.0,
        **kwargs: Any,
    ) -> Any:
        """Executes any callable under an exponential backoff retry policy."""
        delay = initial_delay
        last_exc: Exception | None = None

        for attempt in range(retries):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                self.logger.warning(
                    "Execution failed, retrying...",
                    attempt=attempt + 1,
                    max_attempts=retries,
                    delay=delay,
                    error=str(e),
                )
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= backoff_factor

        raise AgentException(
            f"Execution failed after {retries} attempts."
        ) from last_exc

    @abstractmethod
    async def _run(self, request: AgentRequest, config: ModelConfig) -> Any:
        """Internal runner to execute provider invocations or tools. Implemented by concrete agents."""
        pass

    async def execute(self, request: AgentRequest, config: ModelConfig) -> AgentResult:
        """Orchestrates agent execution flow containing validation, tracing, retries, and metrics compilation."""
        start_time = time.perf_counter()

        self.logger.info(
            "Agent execution started",
            agent_name=self.name,
            request_id=request.execution_context.request_id,
            correlation_id=request.execution_context.correlation_id,
        )

        try:
            self.validate(request)
            # Execute with automatic retries
            output = await self.retry(self._run, request, config)
            duration_ms = (time.perf_counter() - start_time) * 1000

            reasoning = "Completed successfully."
            if isinstance(output, dict):
                reasoning = output.get("reasoning_summary", reasoning)

            result = AgentResult(
                success=True,
                output=output,
                confidence=self.confidence(output),
                reasoning_summary=reasoning,
                metadata={
                    "agent_name": self.name,
                    "provider": config.provider,
                    "model_name": config.model_name,
                    "temperature": config.temperature,
                },
                processing_time_ms=round(duration_ms, 2),
            )

            self.logger.info(
                "Agent execution completed",
                agent_name=self.name,
                processing_time_ms=result.processing_time_ms,
                confidence=result.confidence,
            )
            return result

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.logger.exception(
                "Agent execution crashed",
                agent_name=self.name,
                error=str(e),
            )
            return AgentResult(
                success=False,
                output=str(e),
                confidence=0.0,
                reasoning_summary=f"Agent crashed: {e}",
                metadata={
                    "agent_name": self.name,
                    "error": str(e),
                },
                processing_time_ms=round(duration_ms, 2),
            )
