"""AIOS Structured Logging Configuration."""

import logging
import sys
from typing import Any

import structlog

from aios.core.config import settings


def configure_logging() -> None:
    """Configure structured logging for AIOS."""

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    # Configure structlog
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_format == "json":
        # JSON format for production
        processors = [*shared_processors, structlog.processors.format_exc_info, structlog.processors.JSONRenderer()]
    else:
        # Console format for development
        processors = [*shared_processors, structlog.dev.ConsoleRenderer(colors=True)]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **extra: dict[str, Any],
) -> None:
    """Log an HTTP request."""
    logger = get_logger("aios.request")
    logger.info(
        "HTTP Request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        **extra,
    )


def log_error(
    error: Exception,
    context: str = "",
    **extra: dict[str, Any],
) -> None:
    """Log an error with context."""
    logger = get_logger("aios.error")
    logger.error(
        "Error occurred",
        error=str(error),
        error_type=type(error).__name__,
        context=context,
        **extra,
    )
