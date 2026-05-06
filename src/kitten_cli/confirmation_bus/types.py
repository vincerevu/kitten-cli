"""
Confirmation Bus — Pub/sub message bus for tool confirmations.
Ref: gemini-cli/packages/core/src/confirmation-bus/types.ts
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class MessageBusType(str, Enum):
    TOOL_CONFIRMATION_REQUEST = "tool-confirmation-request"
    TOOL_CONFIRMATION_RESPONSE = "tool-confirmation-response"
    TOOL_POLICY_REJECTION = "tool-policy-rejection"
    TOOL_EXECUTION_SUCCESS = "tool-execution-success"
    TOOL_EXECUTION_FAILURE = "tool-execution-failure"
    UPDATE_POLICY = "update-policy"
    TOOL_CALLS_UPDATE = "tool-calls-update"
    ASK_USER_REQUEST = "ask-user-request"
    ASK_USER_RESPONSE = "ask-user-response"


class ToolConfirmationRequest(BaseModel):
    type: str = MessageBusType.TOOL_CONFIRMATION_REQUEST
    tool_name: str
    tool_args: Dict[str, Any] = {}
    correlation_id: str
    server_name: Optional[str] = None
    tool_annotations: Optional[Dict[str, Any]] = None
    subagent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    forced_decision: Optional[str] = None  # "allow" | "deny" | "ask_user"


class ToolConfirmationResponse(BaseModel):
    type: str = MessageBusType.TOOL_CONFIRMATION_RESPONSE
    correlation_id: str
    confirmed: bool
    outcome: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    requires_user_confirmation: bool = False


class ToolPolicyRejection(BaseModel):
    type: str = MessageBusType.TOOL_POLICY_REJECTION
    tool_name: str
    tool_args: Dict[str, Any] = {}


class ToolExecutionSuccess(BaseModel):
    type: str = MessageBusType.TOOL_EXECUTION_SUCCESS
    tool_name: str
    result: Any = None


class ToolExecutionFailure(BaseModel):
    type: str = MessageBusType.TOOL_EXECUTION_FAILURE
    tool_name: str
    error: str = ""


class UpdatePolicy(BaseModel):
    type: str = MessageBusType.UPDATE_POLICY
    tool_name: str
    persist: bool = False
    persist_scope: Optional[str] = None  # "workspace" | "user"
    args_pattern: Optional[str] = None
    command_prefix: Optional[str] = None
    modes: Optional[List[str]] = None


class QuestionType(str, Enum):
    CHOICE = "choice"
    TEXT = "text"
    YESNO = "yesno"


class QuestionOption(BaseModel):
    label: str
    description: str


class Question(BaseModel):
    question: str
    header: str
    type: QuestionType = QuestionType.TEXT
    options: Optional[List[QuestionOption]] = None
    multi_select: bool = False
    placeholder: Optional[str] = None


class AskUserRequest(BaseModel):
    type: str = MessageBusType.ASK_USER_REQUEST
    questions: List[Question]
    correlation_id: str


class AskUserResponse(BaseModel):
    type: str = MessageBusType.ASK_USER_RESPONSE
    correlation_id: str
    answers: Dict[str, str] = {}
    cancelled: bool = False


class ToolConfirmationOutcome(str, Enum):
    """Outcomes for user confirmation dialogs."""
    PROCEED = "proceed"
    PROCEED_ALWAYS = "proceed_always"
    PROCEED_ALWAYS_AND_SAVE = "proceed_always_and_save"
    PROCEED_ALWAYS_TOOL = "proceed_always_tool"
    PROCEED_ALWAYS_SERVER = "proceed_always_server"
    REJECT = "reject"
    MODIFY_WITH_EDITOR = "modify_with_editor"
