from enum import Enum
from kitten_cli.config.settings import ApprovalMode, AppConfig

class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK_USER = "ask_user"

# Tools that make modifications
EDIT_TOOL_NAMES = {
    "write_file", "edit_file",                           # kitten-cli names
    "multi_replace_file_content", "replace_file_content", "write_to_file",  # gemini-cli compat
}
COMMAND_TOOL_NAMES = {"run_command"}

def check_policy(tool_name: str, args: dict, config: AppConfig) -> PolicyDecision:
    """
    Check if a tool execution is allowed based on the current ApprovalMode.
    """
    mode = config.approval_mode

    # YOLO mode allows everything
    if mode == ApprovalMode.YOLO:
        return PolicyDecision.ALLOW

    # PLAN mode denies edits and commands, allows reads
    if mode == ApprovalMode.PLAN:
        if tool_name in EDIT_TOOL_NAMES or tool_name in COMMAND_TOOL_NAMES:
            return PolicyDecision.DENY
        return PolicyDecision.ALLOW

    # AUTO_EDIT mode allows file edits, asks for commands
    if mode == ApprovalMode.AUTO_EDIT:
        if tool_name in COMMAND_TOOL_NAMES:
            return PolicyDecision.ASK_USER
        return PolicyDecision.ALLOW

    # DEFAULT mode asks for both edits and commands
    if tool_name in EDIT_TOOL_NAMES or tool_name in COMMAND_TOOL_NAMES:
        return PolicyDecision.ASK_USER
        
    # Read-only tools are allowed by default
    return PolicyDecision.ALLOW
