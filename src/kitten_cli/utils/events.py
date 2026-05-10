
import asyncio
from typing import Any, Callable, Dict, List


class EventEmitter:
    """Simple async event emitter."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event: str, listener: Callable) -> None:
        """Subscribe to an event."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)

    def off(self, event: str, listener: Callable) -> None:
        """Unsubscribe from an event."""
        if event in self._listeners:
            try:
                self._listeners[event].remove(listener)
            except ValueError:
                pass

    def once(self, event: str, listener: Callable) -> None:
        """Subscribe to an event, but only fire once."""
        def wrapper(*args, **kwargs):
            self.off(event, wrapper)
            return listener(*args, **kwargs)
        self.on(event, wrapper)

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event to all listeners."""
        for listener in self._listeners.get(event, []):
            result = listener(*args, **kwargs)
            if asyncio.iscoroutine(result):
                await result

    def emit_sync(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event synchronously (no await)."""
        for listener in self._listeners.get(event, []):
            listener(*args, **kwargs)

    def listener_count(self, event: str) -> int:
        return len(self._listeners.get(event, []))

    def remove_all_listeners(self, event: str = "") -> None:
        if event:
            self._listeners.pop(event, None)
        else:
            self._listeners.clear()
