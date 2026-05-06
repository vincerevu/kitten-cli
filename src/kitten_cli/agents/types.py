from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class AgentTerminateMode(str, Enum):
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    GOAL = "GOAL"
    MAX_TURNS = "MAX_TURNS"
    ABORTED = "ABORTED"
    ERROR_NO_COMPLETE_TASK_CALL = "ERROR_NO_COMPLETE_TASK_CALL"

class OutputObject(BaseModel):
    result: str
    terminate_reason: AgentTerminateMode
    turn_count: Optional[int] = None
    duration_ms: Optional[int] = None

DEFAULT_QUERY_STRING = "Get Started!"
DEFAULT_MAX_TURNS = 30
DEFAULT_MAX_TIME_MINUTES = 10

class AgentEventType(str, Enum):
    CONTENT = "content"
    TOOL_CALL_CHUNK = "tool_call_chunk"
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
    INVALID_STREAM = "invalid_stream"
    MODEL_INFO = "model_info"
    AGENT_EXECUTION_STOPPED = "agent_execution_stopped"
    AGENT_EXECUTION_BLOCKED = "agent_execution_blocked"


class AgentEvent(BaseModel):
    type: AgentEventType
    value: Optional[Any] = None
    traceId: Optional[str] = None


class ToolCallRequestInfo(BaseModel):
    callId: str
    name: str
    args: Dict[str, Any]
    display: Optional[Dict[str, Any]] = None
    isClientInitiated: bool = False
    prompt_id: Optional[str] = None
    traceId: Optional[str] = None

class ToolCallResponseInfo(BaseModel):
    callId: str
    name: str
    result: str
    isError: bool = False

class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    max_turns: int = Field(default=DEFAULT_MAX_TURNS)
