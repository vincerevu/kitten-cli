"""
Core type definitions — shared across the codebase.
Ref: gemini-cli/packages/core/src/agents/types.ts
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# Default limits matching gemini-cli
DEFAULT_MAX_TURNS = 30
DEFAULT_MAX_TIME_MINUTES = 10


class ToolCallInfo(BaseModel):
    """Information about a tool call request/response."""
    tool_name: str
    tool_args: Dict[str, Any] = {}
    result: Optional[str] = None
    error: Optional[str] = None
    is_error: bool = False
    duration_ms: Optional[float] = None


class OutputObject(BaseModel):
    """Structured output from the agent."""
    text: str = ""
    tool_calls: List[ToolCallInfo] = []
    thought: Optional[str] = None
    model_info: Optional[Dict[str, Any]] = None


class FinishReason(str, Enum):
    STOP = "stop"
    MAX_TOKENS = "max_tokens"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"
