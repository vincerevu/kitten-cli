"""
Loop detection service — detects when the agent is stuck in a loop.
Ref: gemini-cli/packages/core/src/services/loopDetectionService.ts

Detects patterns like:
- Agent repeatedly calling the same tool with the same args
- Agent producing the same text output multiple times
- Agent alternating between the same 2-3 actions
"""

import hashlib
from collections import deque
from typing import Any, Dict, List, Optional


# Thresholds
MAX_IDENTICAL_TOOL_CALLS = 3      # Same tool+args N times in a row
MAX_SIMILAR_OUTPUTS = 3           # Same output hash N times in recent window
WINDOW_SIZE = 10                  # How many recent actions to track
MAX_OSCILLATION_CYCLES = 3        # A-B-A-B pattern detected after N cycles


class LoopDetectionService:
    """
    Monitors agent actions to detect infinite loops and repetitive behavior.
    When a loop is detected, the agent should be interrupted with a warning.
    """

    def __init__(
        self,
        max_identical_calls: int = MAX_IDENTICAL_TOOL_CALLS,
        max_similar_outputs: int = MAX_SIMILAR_OUTPUTS,
        window_size: int = WINDOW_SIZE,
    ):
        self.max_identical_calls = max_identical_calls
        self.max_similar_outputs = max_similar_outputs
        self.window_size = window_size

        # Tracking state
        self._recent_tool_calls: deque = deque(maxlen=window_size)
        self._recent_output_hashes: deque = deque(maxlen=window_size)
        self._consecutive_identical_count = 0
        self._last_tool_signature: Optional[str] = None
        self._total_turns = 0

    def _hash_content(self, content: str) -> str:
        """Create a short hash of content for comparison."""
        return hashlib.md5(content.encode("utf-8", errors="replace")).hexdigest()[:12]

    def _tool_signature(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Create a deterministic signature for a tool call."""
        # Sort args for consistency
        args_str = str(sorted(tool_args.items())) if tool_args else ""
        return f"{tool_name}:{self._hash_content(args_str)}"

    def record_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> None:
        """Record a tool call for loop detection."""
        sig = self._tool_signature(tool_name, tool_args)
        self._recent_tool_calls.append(sig)

        if sig == self._last_tool_signature:
            self._consecutive_identical_count += 1
        else:
            self._consecutive_identical_count = 1
            self._last_tool_signature = sig

    def record_output(self, content: str) -> None:
        """Record an agent output for loop detection."""
        if content and content.strip():
            h = self._hash_content(content.strip())
            self._recent_output_hashes.append(h)

    def record_turn(self) -> None:
        """Record that a new turn has started."""
        self._total_turns += 1

    def check_loop(self) -> Optional[str]:
        """
        Check if a loop is detected.
        Returns a warning message if loop detected, None otherwise.
        """
        # Check 1: Same tool called N times in a row
        if self._consecutive_identical_count >= self.max_identical_calls:
            return (
                f"Loop detected: The same tool call has been repeated "
                f"{self._consecutive_identical_count} times consecutively. "
                f"Please try a different approach."
            )

        # Check 2: Same output hash appears too frequently in recent window
        if len(self._recent_output_hashes) >= self.max_similar_outputs:
            hashes = list(self._recent_output_hashes)
            for h in set(hashes):
                if hashes.count(h) >= self.max_similar_outputs:
                    return (
                        f"Loop detected: The agent is producing the same output repeatedly "
                        f"({hashes.count(h)} times in the last {len(hashes)} outputs). "
                        f"Please try a different approach."
                    )

        # Check 3: Oscillation (A-B-A-B pattern)
        if len(self._recent_tool_calls) >= MAX_OSCILLATION_CYCLES * 2:
            calls = list(self._recent_tool_calls)
            tail = calls[-(MAX_OSCILLATION_CYCLES * 2):]
            # Check if it's alternating between 2 values
            if len(set(tail)) == 2:
                evens = set(tail[::2])
                odds = set(tail[1::2])
                if len(evens) == 1 and len(odds) == 1 and evens != odds:
                    return (
                        f"Loop detected: The agent is oscillating between two actions. "
                        f"Please try a different approach."
                    )

        return None

    def reset(self) -> None:
        """Reset all tracking state."""
        self._recent_tool_calls.clear()
        self._recent_output_hashes.clear()
        self._consecutive_identical_count = 0
        self._last_tool_signature = None
        self._total_turns = 0

    @property
    def stats(self) -> Dict[str, Any]:
        """Get current loop detection stats."""
        return {
            "total_turns": self._total_turns,
            "consecutive_identical": self._consecutive_identical_count,
            "recent_tool_calls": len(self._recent_tool_calls),
            "recent_outputs": len(self._recent_output_hashes),
            "unique_recent_tools": len(set(self._recent_tool_calls)),
        }
