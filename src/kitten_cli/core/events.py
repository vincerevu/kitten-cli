"""
Core event types for kitten-cli.
Ref: gemini-cli/packages/core/src/core/turn.ts — GeminiEventType
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AgentEventType(str, Enum):
    """All event types emitted by the agent loop."""
    CONTENT = "content"
    TOOL_CALL_REQUEST = "tool_call_request"
    TOOL_CALL_RESPONSE = "tool_call_response"
    TOOL_CALL_CONFIRMATION = "tool_call_confirmation"
    USER_CANCELLED = "user_cancelled"
    ERROR = "error"
    CHAT_COMPRESSED = "chat_compressed"
    THOUGHT = "thought"
    MAX_SESSION_TURNS = "max_session_turns"
    FINISHED = "finished"
    LOOP_DETECTED = "loop_detected"
    CITATION = "citation"
    RETRY = "retry"
    CONTEXT_WINDOW_WILL_OVERFLOW = "context_window_will_overflow"
    MODEL_INFO = "model_info"
    AGENT_EXECUTION_STOPPED = "agent_execution_stopped"
    AGENT_EXECUTION_BLOCKED = "agent_execution_blocked"


class AgentEvent(BaseModel):
    """A single event emitted from the agent loop."""
    type: AgentEventType
    content: str = ""
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class AgentTerminateMode(str, Enum):
    """How the agent loop terminated."""
    COMPLETED = "completed"
    MAX_TURNS = "max_turns"
    MAX_TIME = "max_time"
    USER_CANCELLED = "user_cancelled"
    ERROR = "error"
    LOOP_DETECTED = "loop_detected"
    CONTEXT_OVERFLOW = "context_overflow"


class RunConfig(BaseModel):
    """Configuration for a single agent run."""
    max_turns: int = 30
    max_time_minutes: int = 10
    system_prompt: str = ""
    tools_enabled: bool = True
    model: str = ""
    temperature: float = 0.7
