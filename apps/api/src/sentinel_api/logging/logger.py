import logging
import sys

import structlog
from structlog.types import Processor

from sentinel_api.config.settings import settings


def setup_logging() -> None:
    """Configures structlog to output structured logs.

    In production, logs are formatted as JSON.
    In development, logs are colorized and formatted for console readability.
    """
    # Map string log level to python logging level
    log_level = logging.getLevelName(settings.LOG_LEVEL.upper())
    if isinstance(log_level, str):
        # Fallback if invalid string is provided
        log_level = logging.INFO

    # Shared processors for both stdout/stderr and structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.is_dev:
        # Dev console logging
        processors = [*shared_processors, structlog.dev.ConsoleRenderer()]
    else:
        # Production JSON logging
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )

    # Intercept standard library logging if needed
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Helper function to retrieve a bound structlog logger."""
    return structlog.get_logger(name)
