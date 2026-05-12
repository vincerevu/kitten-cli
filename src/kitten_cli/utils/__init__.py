"""Shared utilities."""

from kitten_cli.utils.errors import (
    KittenError,
    UnauthorizedError,
    RateLimitError,
    ModelNotFoundError,
    ToolExecutionError,
    PolicyViolationError,
    ContextOverflowError,
)
from kitten_cli.utils.events import EventEmitter
from kitten_cli.utils.ignore_patterns import IgnorePatterns

__all__ = [
    "KittenError",
    "UnauthorizedError",
    "RateLimitError",
    "ModelNotFoundError",
    "ToolExecutionError",
    "PolicyViolationError",
    "ContextOverflowError",
    "EventEmitter",
    "IgnorePatterns",
]
