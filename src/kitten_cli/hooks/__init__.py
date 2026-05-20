"""
Hook system — lifecycle hooks for extending agent behavior.
Ref: gemini-cli/packages/core/src/hooks/

Hooks allow plugins and extensions to tap into the agent lifecycle:
  - on_session_start    — Called when a new session begins
  - on_session_end      — Called when a session ends
  - on_turn_start       — Called before each agent turn
  - on_turn_end         — Called after each agent turn
  - on_tool_call        — Called before a tool is executed
  - on_tool_result      — Called after a tool returns
  - on_model_request    — Called before sending to the LLM
  - on_model_response   — Called after receiving LLM response
  - on_error            — Called when an error occurs
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class HookEvent(str, Enum):
    """Hook lifecycle events."""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TURN_START = "turn_start"
    TURN_END = "turn_end"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    MODEL_REQUEST = "model_request"
    MODEL_RESPONSE = "model_response"
    ERROR = "error"
    CONTEXT_COMPACT = "context_compact"
    CHECKPOINT_CREATE = "checkpoint_create"
    CHECKPOINT_RESTORE = "checkpoint_restore"


# Type alias for hook handlers
HookHandler = Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]


class HookRegistry:
    """
    Registry for lifecycle hooks.
    Hooks are executed in registration order. A hook can optionally
    modify the event data by returning a new dict.
    """

    def __init__(self):
        self._hooks: Dict[HookEvent, List[HookHandler]] = {
            event: [] for event in HookEvent
        }

    def register(self, event: HookEvent, handler: HookHandler) -> None:
        """Register a hook handler for an event."""
        self._hooks[event].append(handler)

    def unregister(self, event: HookEvent, handler: HookHandler) -> bool:
        """Unregister a hook handler. Returns True if found and removed."""
        try:
            self._hooks[event].remove(handler)
            return True
        except ValueError:
            return False

    def emit(self, event: HookEvent, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Emit an event, calling all registered handlers in order.
        Each handler receives the event data and can optionally return modified data.
        Returns the final (possibly modified) data.
        """
        current_data = data or {}

        for handler in self._hooks[event]:
            try:
                result = handler(current_data)
                if result is not None and isinstance(result, dict):
                    current_data = result
            except Exception:
                # Hooks should not crash the agent
                pass

        return current_data

    async def emit_async(self, event: HookEvent, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Async version of emit for async hook handlers.
        Supports both sync and async handlers.
        """
        import asyncio
        current_data = data or {}

        for handler in self._hooks[event]:
            try:
                result = handler(current_data)
                if asyncio.iscoroutine(result):
                    result = await result
                if result is not None and isinstance(result, dict):
                    current_data = result
            except Exception:
                pass

        return current_data

    def has_hooks(self, event: HookEvent) -> bool:
        """Check if any hooks are registered for an event."""
        return len(self._hooks[event]) > 0

    def clear(self, event: Optional[HookEvent] = None) -> None:
        """Clear hooks for a specific event, or all hooks."""
        if event:
            self._hooks[event] = []
        else:
            for e in HookEvent:
                self._hooks[e] = []

    def get_hook_count(self, event: Optional[HookEvent] = None) -> int:
        """Get count of registered hooks."""
        if event:
            return len(self._hooks[event])
        return sum(len(h) for h in self._hooks.values())

    @property
    def stats(self) -> Dict[str, int]:
        """Get hook registration stats."""
        return {
            event.value: len(handlers)
            for event, handlers in self._hooks.items()
            if handlers
        }


# Global hook registry instance
_global_registry: Optional[HookRegistry] = None


def get_hook_registry() -> HookRegistry:
    """Get the global hook registry (lazy singleton)."""
    global _global_registry
    if _global_registry is None:
        _global_registry = HookRegistry()
    return _global_registry


def on(event: HookEvent) -> Callable:
    """
    Decorator to register a function as a hook handler.
    
    Usage:
        @on(HookEvent.TURN_START)
        def my_hook(data):
            print(f"Turn started: {data}")
    """
    def decorator(func: HookHandler) -> HookHandler:
        get_hook_registry().register(event, func)
        return func
    return decorator
