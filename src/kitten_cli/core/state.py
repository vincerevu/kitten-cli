
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SessionState(BaseModel):
    """Tracks the state of a single agent session."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    start_time: float = Field(default_factory=time.time)
    turn_count: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    tool_calls_count: int = 0
    errors_count: int = 0
    is_compressed: bool = False
    history: List[Dict[str, Any]] = Field(default_factory=list)

    def add_message(self, message: Any) -> None:
        if hasattr(message, "model_dump"):
            self.history.append(message.model_dump())
        else:
            self.history.append(message)

    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    @property
    def elapsed_minutes(self) -> float:
        return self.elapsed_seconds / 60

    def add_turn(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.turn_count += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

    def add_tool_call(self) -> None:
        self.tool_calls_count += 1

    def add_error(self) -> None:
        self.errors_count += 1

    def to_stats(self) -> Dict[str, Any]:
        """Return session statistics for /stats command."""
        return {
            "session_id": self.session_id[:8],
            "duration": f"{self.elapsed_minutes:.1f}m",
            "turns": self.turn_count,
            "tool_calls": self.tool_calls_count,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "errors": self.errors_count,
            "compressed": self.is_compressed,
        }
