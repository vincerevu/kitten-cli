"""
Retry utilities with exponential backoff.
Ref: gemini-cli/packages/core/src/utils/retry.ts

Provides retry decorators and functions for handling transient failures
in LLM API calls, network requests, and tool executions.
"""

import asyncio
import random
from typing import Any, Callable, Optional, Set, Type, TypeVar

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay_ms: int = 1000,
        max_delay_ms: int = 30_000,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[Set[Type[Exception]]] = None,
        retryable_status_codes: Optional[Set[int]] = None,
    ):
        self.max_retries = max_retries
        self.initial_delay_ms = initial_delay_ms
        self.max_delay_ms = max_delay_ms
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or {
            ConnectionError,
            TimeoutError,
            OSError,
        }
        self.retryable_status_codes = retryable_status_codes or {
            429, 500, 502, 503, 504,
        }


# Default configs for common use cases
LLM_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    initial_delay_ms=2000,
    max_delay_ms=60_000,
    retryable_status_codes={429, 500, 502, 503, 504, 529},
)

NETWORK_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    initial_delay_ms=500,
    max_delay_ms=10_000,
)


def _calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay in seconds for a retry attempt."""
    delay_ms = config.initial_delay_ms * (config.backoff_factor ** attempt)
    delay_ms = min(delay_ms, config.max_delay_ms)

    if config.jitter:
        delay_ms = delay_ms * (0.5 + random.random())

    return delay_ms / 1000.0


def _is_retryable(error: Exception, config: RetryConfig) -> bool:
    """Check if an error is retryable."""
    # Check exception type
    for exc_type in config.retryable_exceptions:
        if isinstance(error, exc_type):
            return True

    # Check for HTTP status codes in the error
    status_code = getattr(error, "status_code", None) or getattr(error, "status", None)
    if status_code and status_code in config.retryable_status_codes:
        return True

    # Check error message for common transient patterns
    msg = str(error).lower()
    transient_patterns = ["rate limit", "quota", "too many requests", "overloaded", "temporarily"]
    return any(p in msg for p in transient_patterns)


async def retry_async(
    func: Callable,
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable] = None,
) -> Any:
    """
    Execute an async function with retry logic.
    
    Args:
        func: Async callable to retry
        config: Retry configuration
        on_retry: Optional callback(attempt, error, delay) called before each retry
    """
    cfg = config or RetryConfig()
    last_error = None

    for attempt in range(cfg.max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_error = e

            if attempt >= cfg.max_retries:
                break

            if not _is_retryable(e, cfg):
                break

            delay = _calculate_delay(attempt, cfg)

            if on_retry:
                try:
                    on_retry(attempt + 1, e, delay)
                except Exception:
                    pass

            await asyncio.sleep(delay)

    raise last_error


def retry_sync(
    func: Callable,
    config: Optional[RetryConfig] = None,
) -> Any:
    """
    Execute a sync function with retry logic.
    """
    import time as _time

    cfg = config or RetryConfig()
    last_error = None

    for attempt in range(cfg.max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_error = e

            if attempt >= cfg.max_retries:
                break

            if not _is_retryable(e, cfg):
                break

            delay = _calculate_delay(attempt, cfg)
            _time.sleep(delay)

    raise last_error
