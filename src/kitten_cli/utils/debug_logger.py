"""
Debug logger for development and troubleshooting.
Ref: gemini-cli/packages/core/src/utils/debugLogger.ts

Controlled via KITTEN_DEBUG environment variable:
  KITTEN_DEBUG=1        — enable all debug output
  KITTEN_DEBUG=tool     — only tool-related debug
  KITTEN_DEBUG=context  — only context-related debug
"""

import os
import sys
import time
from typing import Optional


class DebugLogger:
    """
    Debug logger that writes to stderr.
    Only outputs when KITTEN_DEBUG env var is set.
    """

    def __init__(self, namespace: str = ""):
        self.namespace = namespace
        self._enabled: Optional[bool] = None

    @property
    def enabled(self) -> bool:
        """Check if debug logging is enabled."""
        if self._enabled is None:
            debug_val = os.environ.get("KITTEN_DEBUG", "").lower()
            if not debug_val:
                self._enabled = False
            elif debug_val in ("1", "true", "all"):
                self._enabled = True
            elif self.namespace and debug_val == self.namespace:
                self._enabled = True
            else:
                self._enabled = False
        return self._enabled

    def log(self, message: str, *args) -> None:
        """Log a debug message to stderr."""
        if not self.enabled:
            return
        timestamp = time.strftime("%H:%M:%S")
        prefix = f"[{timestamp}] [{self.namespace}]" if self.namespace else f"[{timestamp}]"
        formatted = message % args if args else message
        print(f"{prefix} {formatted}", file=sys.stderr)

    def warn(self, message: str, *args) -> None:
        """Log a warning."""
        if not self.enabled:
            return
        self.log(f"WARN: {message}", *args)

    def error(self, message: str, *args) -> None:
        """Log an error (always outputs if debug is enabled)."""
        if not self.enabled:
            return
        self.log(f"ERROR: {message}", *args)

    def child(self, sub_namespace: str) -> "DebugLogger":
        """Create a child logger with a sub-namespace."""
        ns = f"{self.namespace}.{sub_namespace}" if self.namespace else sub_namespace
        return DebugLogger(ns)


# Pre-built loggers for common subsystems
debug_logger = DebugLogger("kitten")
tool_logger = DebugLogger("tool")
context_logger = DebugLogger("context")
llm_logger = DebugLogger("llm")
