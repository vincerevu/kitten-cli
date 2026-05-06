"""Quick import verification test."""
from kitten_cli.tools import create_default_registry
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult, ToolErrorType
from kitten_cli.confirmation_bus.types import MessageBusType, ToolConfirmationRequest
from kitten_cli.confirmation_bus.bus import MessageBus
from kitten_cli.core.events import AgentEventType, AgentEvent, AgentTerminateMode, RunConfig
from kitten_cli.core.state import SessionState
from kitten_cli.core.types import DEFAULT_MAX_TURNS, ToolCallInfo
from kitten_cli.core.token_limits import get_context_window, should_compress
from kitten_cli.utils.errors import KittenError, UnauthorizedError, RateLimitError
from kitten_cli.utils.paths import get_kitten_dir, normalize_path
from kitten_cli.utils.files import read_file_safe, is_binary_file
from kitten_cli.utils.text import truncate_text, count_tokens_estimate
from kitten_cli.utils.diff import generate_unified_diff, generate_diff_stat
from kitten_cli.utils.shell_utils import extract_root_command, get_shell_info
from kitten_cli.utils.ignore_patterns import IgnorePatterns
from kitten_cli.utils.events import EventEmitter
from kitten_cli.utils.json import safe_json_dumps, safe_json_loads

r = create_default_registry("d:/kitten-cli")
print(f"OK: {r.count()} tools: {r.get_names()}")
print(f"ctx gpt4o={get_context_window('gpt-4o')} gemini={get_context_window('gemini-2.5-pro')}")
print(f"shell={get_shell_info()}")
print(f"DEFAULT_MAX_TURNS={DEFAULT_MAX_TURNS}")
