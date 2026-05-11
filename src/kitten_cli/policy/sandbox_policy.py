
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from kitten_cli.policy.engine import PolicyEngine
from kitten_cli.policy.types import (
    CheckResult,
    COMMAND_TOOL_NAMES,
    EDIT_TOOL_NAMES,
    PermissionDecision,
)


@dataclass
class SandboxPolicy:
    """Configuration for sandbox mode."""

    # If true, sandbox is active
    enabled: bool = False

    # Allowed commands that can bypass sandbox (exact prefix match)
    allowed_commands: List[str] = field(default_factory=list)

    # Directories/patterns that are writable (glob)
    writable_paths: List[str] = field(default_factory=list)


class SandboxPolicyManager:
    """
    Wraps PolicyEngine with additional sandbox constraints.

    When sandbox is enabled:
      - Shell commands are denied unless they match allowed_commands prefix
      - File edits are denied unless the target path matches writable_paths globs
    """

    def __init__(
        self,
        engine: PolicyEngine,
        sandbox_policy: Optional[SandboxPolicy] = None,
    ) -> None:
        self._engine = engine
        self._policy = sandbox_policy or SandboxPolicy()

    @property
    def engine(self) -> PolicyEngine:
        return self._engine

    @property
    def is_enabled(self) -> bool:
        return self._policy.enabled

    # ------------------------------------------------------------------
    # Sandbox checks
    # ------------------------------------------------------------------

    def is_command_allowed(self, command: str) -> bool:
        """Check if a command is allowed to run outside sandbox."""
        if not self._policy.enabled:
            return True

        return any(
            command.startswith(allowed) or command == allowed
            for allowed in self._policy.allowed_commands
        )

    def is_path_writable(self, file_path: str) -> bool:
        """Check if a file path is writable in sandbox mode."""
        if not self._policy.enabled:
            return True

        for pattern in self._policy.writable_paths:
            if pattern == "*":
                return True
            if pattern.endswith("/**"):
                dir_prefix = pattern[:-3]
                if file_path.startswith(dir_prefix):
                    return True
            elif fnmatch.fnmatch(file_path, pattern):
                return True
            elif file_path == pattern:
                return True

        return False

    # ------------------------------------------------------------------
    # Main check: engine + sandbox
    # ------------------------------------------------------------------

    def check(self, tool_name: str, args: Optional[Dict[str, Any]] = None) -> CheckResult:
        """
        Wrap the engine check with sandbox constraints.

        1. Run PolicyEngine.check() first
        2. If engine allows AND sandbox is enabled → apply sandbox restrictions
        """
        args = args or {}

        # First: policy engine check
        result = self._engine.check(tool_name, args)

        # If sandbox is not enabled or engine already denied/asked, return as-is
        if not self._policy.enabled or result.decision != PermissionDecision.ALLOW:
            return result

        # Sandbox is enabled and engine said ALLOW — apply additional restrictions

        # For shell commands, check command allowlist
        if tool_name in COMMAND_TOOL_NAMES:
            cmd = str(args.get("command", args.get("CommandLine", "")))
            if not self.is_command_allowed(cmd):
                return CheckResult(
                    tool=tool_name,
                    decision=PermissionDecision.DENY,
                    reason=f"Sandbox: command not in allowlist: {cmd}",
                )

        # For file edits, check writable paths
        if tool_name in EDIT_TOOL_NAMES:
            file_path = str(args.get("file_path", args.get("TargetFile", "")))
            if not self.is_path_writable(file_path):
                return CheckResult(
                    tool=tool_name,
                    decision=PermissionDecision.DENY,
                    reason=f"Sandbox: path not writable: {file_path}",
                )

        return result

    # ------------------------------------------------------------------
    # Enable/disable
    # ------------------------------------------------------------------

    def enable(self, policy: Optional[SandboxPolicy] = None) -> None:
        """Enable sandbox mode."""
        if policy:
            self._policy = policy
        else:
            self._policy = SandboxPolicy(
                enabled=True,
                allowed_commands=[],
                writable_paths=["*"],  # default: all paths writable
            )

    def disable(self) -> None:
        """Disable sandbox mode."""
        self._policy.enabled = False
