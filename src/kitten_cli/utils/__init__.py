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
from kitten_cli.utils.token_counting import (
    estimate_tokens,
    estimate_message_tokens,
    estimate_history_tokens,
    check_context_limit,
)
from kitten_cli.utils.debug_logger import DebugLogger, debug_logger
from kitten_cli.utils.retry import retry_async, retry_sync, RetryConfig, LLM_RETRY_CONFIG
from kitten_cli.utils.environment_context import get_environment_context, format_environment_context

__all__ = [
    # Errors
    "KittenError",
    "UnauthorizedError",
    "RateLimitError",
    "ModelNotFoundError",
    "ToolExecutionError",
    "PolicyViolationError",
    "ContextOverflowError",
    # Events
    "EventEmitter",
    # Patterns
    "IgnorePatterns",
    # Token counting
    "estimate_tokens",
    "estimate_message_tokens",
    "estimate_history_tokens",
    "check_context_limit",
    # Debug
    "DebugLogger",
    "debug_logger",
    # Retry
    "retry_async",
    "retry_sync",
    "RetryConfig",
    "LLM_RETRY_CONFIG",
    # Environment
    "get_environment_context",
    "format_environment_context",
]
