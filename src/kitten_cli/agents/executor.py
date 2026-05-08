
import json
import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional

from kitten_cli.llm.client import KittenLLM
from kitten_cli.agents.types import (
    AgentEvent, AgentEventType,
    ToolCallRequestInfo, ToolCallResponseInfo,
    DEFAULT_MAX_TURNS,
)
from kitten_cli.agents.confirmation import PolicyDecision, check_policy
from kitten_cli.config.settings import AppConfig
from kitten_cli.tools.base import DeclarativeTool, ToolResult
from kitten_cli.tools.registry import ToolRegistry
from kitten_cli.confirmation_bus.bus import MessageBus
from kitten_cli.confirmation_bus.types import (
    MessageBusType,
    ToolConfirmationRequest,
    ToolConfirmationResponse,
)


class AgentExecutor:
    """
    Single-agent executor with policy-aware tool execution.
    Yields AgentEvent stream for UI consumption.
    """

    def __init__(
        self,
        config: AppConfig,
        tool_registry: Optional[ToolRegistry] = None,
        message_bus: Optional[MessageBus] = None,
        max_turns: int = DEFAULT_MAX_TURNS,
    ):
        self.config = config
        self.llm = KittenLLM()
        self.registry = tool_registry or ToolRegistry()
        self.bus = message_bus or MessageBus(config)
        self.max_turns = max_turns

    async def run(
        self, messages: List[Dict[str, Any]]
    ) -> AsyncGenerator[AgentEvent, None]:
        """Run the agent loop, yielding events for each step."""
        history = list(messages)
        tool_schemas = self.registry.get_schemas() or None

        for turn in range(self.max_turns):
            text_buffer = ""
            tool_calls_buffer: Dict[int, dict] = {}

            # --- Stream LLM response ---
            async for event in self.llm.stream(
                messages=history,
                tools=tool_schemas,
            ):
                if event.type == AgentEventType.CONTENT:
                    text_buffer += event.value
                    yield event

                elif event.type == AgentEventType.TOOL_CALL_CHUNK:
                    data = event.value
                    idx = data.index or 0
                    if idx not in tool_calls_buffer:
                        tool_calls_buffer[idx] = {
                            "id": data.id or "",
                            "name": "",
                            "arguments": "",
                        }
                    if data.function.name:
                        tool_calls_buffer[idx]["name"] += data.function.name
                    if data.function.arguments:
                        tool_calls_buffer[idx]["arguments"] += data.function.arguments

                elif event.type == AgentEventType.ERROR:
                    yield event
                    return

            # --- No tool calls → agent finished ---
            if not tool_calls_buffer:
                yield AgentEvent(type=AgentEventType.FINISHED)
                return

            # --- Append assistant message with tool calls ---
            tool_calls_list = list(tool_calls_buffer.values())
            history.append({
                "role": "assistant",
                "content": text_buffer or None,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": tc["arguments"],
                        },
                    }
                    for tc in tool_calls_list
                ],
            })

            # --- Execute each tool call with policy check ---
            for tc in tool_calls_list:
                tool_name = tc["name"]
                req_args = {}
                if tc["arguments"]:
                    try:
                        parsed = json.loads(tc["arguments"])
                        if not isinstance(parsed, dict):
                            raise ValueError(f"Expected dict, got {type(parsed).__name__}")
                        req_args = parsed
                    except (json.JSONDecodeError, ValueError) as ex:
                        # Return error to LLM so it can retry with valid args
                        error_msg = f"Error: Invalid tool arguments for '{tool_name}': {ex}"
                        res_info = ToolCallResponseInfo(
                            callId=tc["id"], name=tool_name,
                            result=error_msg, isError=True,
                        )
                        yield AgentEvent(type=AgentEventType.TOOL_CALL_RESPONSE, value=res_info)
                        history.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": error_msg,
                        })
                        continue

                # Emit TOOL_CALL_REQUEST
                req_info = ToolCallRequestInfo(
                    callId=tc["id"],
                    name=tool_name,
                    args=req_args,
                )
                yield AgentEvent(type=AgentEventType.TOOL_CALL_REQUEST, value=req_info)

                # --- Phase 1.7: Policy check ---
                decision = check_policy(tool_name, req_args, self.config)

                if decision == PolicyDecision.DENY:
                    result_str = f"Error: Tool '{tool_name}' denied by policy (mode={self.config.approval_mode})."
                    is_error = True

                elif decision == PolicyDecision.ASK_USER:
                    # Yield confirmation event for UI
                    yield AgentEvent(
                        type=AgentEventType.TOOL_CALL_CONFIRMATION,
                        value={
                            "callId": tc["id"],
                            "tool_name": tool_name,
                            "tool_args": req_args,
                        },
                    )

                    # Wait for user response via message bus
                    try:
                        response = await self.bus.request(
                            tool_name=tool_name,
                            tool_args=req_args,
                            timeout_seconds=300.0,  # 5 min timeout
                        )
                        if not response.confirmed:
                            result_str = f"Tool '{tool_name}' rejected by user."
                            is_error = True
                        else:
                            # User approved → execute
                            result_str, is_error = await self._execute_tool(tool_name, req_args)
                    except asyncio.TimeoutError:
                        result_str = f"Tool '{tool_name}' timed out waiting for user confirmation."
                        is_error = True

                elif decision == PolicyDecision.ALLOW:
                    result_str, is_error = await self._execute_tool(tool_name, req_args)

                else:
                    result_str = f"Error: Unknown policy decision for '{tool_name}'."
                    is_error = True

                # Emit TOOL_CALL_RESPONSE
                res_info = ToolCallResponseInfo(
                    callId=tc["id"],
                    name=tool_name,
                    result=result_str,
                    isError=is_error,
                )
                yield AgentEvent(type=AgentEventType.TOOL_CALL_RESPONSE, value=res_info)

                # Append tool result to history
                history.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_str,
                })

        # Exhausted all turns
        yield AgentEvent(type=AgentEventType.MAX_SESSION_TURNS)

    async def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> tuple:
        """Execute a tool and return (result_str, is_error)."""
        tool = self.registry.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found.", True

        try:
            result = await tool.safe_execute(**args)
            return result.llm_content, result.is_error
        except Exception as ex:
            return f"Tool execution error: {ex}", True