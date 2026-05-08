"""
Output renderers — format AgentEvents for terminal display.
Ref: gemini-cli/packages/core/src/output/outputManager.ts
"""
from typing import Any

from kitten_cli.agents.types import AgentEvent, AgentEventType, ToolCallRequestInfo, ToolCallResponseInfo
from kitten_cli.ui.console import (
    get_console,
    print_markdown,
    print_error,
    print_success,
    print_tool_call,
    print_thinking,
    print_warning,
)
from kitten_cli.utils.json import safe_json_dumps


def render_event(event: AgentEvent) -> None:
    """Render a single AgentEvent to the terminal."""
    handler = _HANDLERS.get(event.type)
    if handler:
        handler(event)


def _render_content(event: AgentEvent) -> None:
    """Render streamed text content (printed inline, no newline)."""
    if event.value:
        get_console().print(event.value, end="", highlight=False)


def _render_tool_request(event: AgentEvent) -> None:
    """Render a tool call request."""
    if isinstance(event.value, ToolCallRequestInfo):
        args_str = safe_json_dumps(event.value.args, indent=0)
        # Truncate long args for display
        if len(args_str) > 120:
            args_str = args_str[:117] + "..."
        print_tool_call(event.value.name, args_str)
    elif isinstance(event.value, dict):
        print_tool_call(event.value.get("name", "?"))


def _render_tool_response(event: AgentEvent) -> None:
    """Render a tool call response."""
    if isinstance(event.value, ToolCallResponseInfo):
        if event.value.isError:
            print_error(f"{event.value.name}: {event.value.result[:200]}")
        else:
            # Show truncated result
            result = event.value.result
            if len(result) > 200:
                result = result[:197] + "..."
            print_success(f"{event.value.name} done ({len(event.value.result)} chars)")


def _render_tool_confirmation(event: AgentEvent) -> None:
    """Render a tool confirmation request (waiting for user approval)."""
    if isinstance(event.value, dict):
        print_warning(f"Approval needed: {event.value.get('tool_name', '?')}")


def _render_thought(event: AgentEvent) -> None:
    if event.value:
        print_thinking(str(event.value))


def _render_error(event: AgentEvent) -> None:
    print_error(str(event.value) if event.value else "Unknown error")


def _render_finished(event: AgentEvent) -> None:
    get_console().print()  # newline after stream


def _render_max_turns(event: AgentEvent) -> None:
    print_warning("Reached maximum turns limit.")


# Event type → handler mapping
_HANDLERS = {
    AgentEventType.CONTENT: _render_content,
    AgentEventType.TOOL_CALL_REQUEST: _render_tool_request,
    AgentEventType.TOOL_CALL_RESPONSE: _render_tool_response,
    AgentEventType.TOOL_CALL_CONFIRMATION: _render_tool_confirmation,
    AgentEventType.THOUGHT: _render_thought,
    AgentEventType.ERROR: _render_error,
    AgentEventType.FINISHED: _render_finished,
    AgentEventType.MAX_SESSION_TURNS: _render_max_turns,
}
