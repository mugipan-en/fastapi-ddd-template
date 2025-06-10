"""Logging configuration."""

import logging
import sys

import structlog
from structlog.types import EventDict

from app.core.config import settings


def add_severity_level(
    logger: logging.Logger, name: str, record: EventDict
) -> EventDict:
    """Add severity level to log record."""
    record["severity"] = record["level"].upper()
    return record


def setup_logging() -> None:
    """Configure structured logging."""

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )

    # Configure structlog
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_severity_level,
    ]

    if settings.LOG_FORMAT == "json":
        # JSON logging for production
        structlog.configure(
            processors=[*shared_processors, structlog.processors.JSONRenderer()],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Human-readable logging for development
        structlog.configure(
            processors=[*shared_processors, structlog.dev.ConsoleRenderer(colors=True)],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get a structured logger."""
    return structlog.get_logger(name)
