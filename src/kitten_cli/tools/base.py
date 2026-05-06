"""
Base tool framework.
Ref: gemini-cli/packages/core/src/tools/tools.ts — DeclarativeTool, ToolResult
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional


class ToolKind(str, Enum):
    """Tool categorization for permissions."""
    READ = "read"          # read_file, ls, grep, glob
    EDIT = "edit"          # edit, write_file
    EXEC = "exec"          # shell, run_command
    SEARCH = "search"      # web_search, web_fetch
    INFO = "info"          # ask_user, complete_task
    MEMORY = "memory"      # memory_tool
    PLAN = "plan"          # enter_plan_mode, exit_plan_mode
    MCP = "mcp"            # mcp tools


READ_ONLY_KINDS = [ToolKind.READ, ToolKind.SEARCH, ToolKind.INFO]


class ToolErrorType(str, Enum):
    INVALID_TOOL_PARAMS = "invalid_tool_params"
    EXECUTION_FAILED = "execution_failed"
    POLICY_VIOLATION = "policy_violation"
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"


class ToolResult:
    """Result of a tool execution."""
    def __init__(
        self,
        llm_content: str,
        return_display: str = "",
        error: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.llm_content = llm_content
        self.return_display = return_display or llm_content
        self.error = error
        self.data = data

    @property
    def is_error(self) -> bool:
        return self.error is not None


class DeclarativeTool(ABC):
    """
    Base class for all tools. Matches gemini-cli's DeclarativeTool.
    
    Subclasses must implement:
    - execute(params) → ToolResult
    - schema (property) → dict (JSON Schema for function calling)
    """

    def __init__(
        self,
        name: str,
        display_name: str,
        description: str,
        kind: ToolKind,
        parameter_schema: Dict[str, Any],
        is_output_markdown: bool = True,
        can_update_output: bool = False,
    ):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.kind = kind
        self.parameter_schema = parameter_schema
        self.is_output_markdown = is_output_markdown
        self.can_update_output = can_update_output

    @property
    def is_read_only(self) -> bool:
        return self.kind in READ_ONLY_KINDS

    @property
    def schema(self) -> Dict[str, Any]:
        """Return the function declaration schema for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameter_schema,
            },
        }

    def validate_params(self, params: Dict[str, Any]) -> Optional[str]:
        """
        Validate raw parameters from the model.
        Returns error message string if invalid, None if ok.
        """
        return None

    @abstractmethod
    async def execute(self, **params: Any) -> ToolResult:
        """Execute the tool with validated parameters."""
        ...

    async def safe_execute(self, **params: Any) -> ToolResult:
        """Execute with error catching — never throws."""
        validation_error = self.validate_params(params)
        if validation_error:
            return ToolResult(
                llm_content=f"Error: Invalid parameters. {validation_error}",
                error={
                    "message": validation_error,
                    "type": ToolErrorType.INVALID_TOOL_PARAMS,
                },
            )
        try:
            return await self.execute(**params)
        except Exception as ex:
            return ToolResult(
                llm_content=f"Error: Tool execution failed. {ex}",
                error={
                    "message": str(ex),
                    "type": ToolErrorType.EXECUTION_FAILED,
                },
            )
