
from typing import Optional


class KittenError(Exception):
    """Base error for all kitten-cli errors."""
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.code = code


class UnauthorizedError(KittenError):
    """API key invalid or expired."""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, code="UNAUTHORIZED")


class RateLimitError(KittenError):
    """API rate limit exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[float] = None):
        super().__init__(message, code="RATE_LIMIT")
        self.retry_after = retry_after


class ModelNotFoundError(KittenError):
    """Requested model not available."""
    def __init__(self, model: str):
        super().__init__(f"Model not found: {model}", code="MODEL_NOT_FOUND")
        self.model = model


class ToolExecutionError(KittenError):
    """Tool execution failed."""
    def __init__(self, tool_name: str, message: str):
        super().__init__(f"Tool '{tool_name}' failed: {message}", code="TOOL_ERROR")
        self.tool_name = tool_name


class PolicyViolationError(KittenError):
    """Action denied by policy."""
    def __init__(self, tool_name: str, message: str = ""):
        super().__init__(
            f"Policy violation for '{tool_name}': {message}" if message else f"Action denied: {tool_name}",
            code="POLICY_VIOLATION",
        )
        self.tool_name = tool_name


class ContextOverflowError(KittenError):
    """Context window is full."""
    def __init__(self, message: str = "Context window overflow"):
        super().__init__(message, code="CONTEXT_OVERFLOW")


def get_error_message(error: Exception) -> str:
    """Extract a clean error message from any exception."""
    if isinstance(error, KittenError):
        return str(error)
    return str(error) or type(error).__name__


def to_friendly_error(error: Exception) -> str:
    """Convert an exception to a user-friendly message."""
    msg = get_error_message(error)
    if isinstance(error, UnauthorizedError):
        return "Authentication failed. Please check your API key."
    if isinstance(error, RateLimitError):
        return f"Rate limit exceeded. Please wait and try again. {msg}"
    if isinstance(error, ModelNotFoundError):
        return f"The requested model is not available: {error.model}"
    return msg
