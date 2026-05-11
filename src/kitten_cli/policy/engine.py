
from __future__ import annotations

import fnmatch
import re
from typing import Any, Dict, List, Optional

from kitten_cli.policy.types import (
    ApprovalMode,
    CheckResult,
    PermissionDecision,
    PolicyRule,
    PolicySettings,
    get_built_in_rules_for_mode,
)


class PolicyEngine:
    """
    Evaluates tool calls against a prioritized list of PolicyRule objects.

    Rule order:
      1. Built-in rules for the current ApprovalMode (low priority: -100, -90)
      2. Additional global policies from ~/.kitten/policies/*.toml
      3. Additional project policies from <workspace>/.kitten/policies/*.toml
      4. Runtime rules added via addRule() (high priority: 100+)

    First match wins (rules sorted by priority descending).
    """

    def __init__(self, settings: Optional[PolicySettings] = None) -> None:
        self._settings = settings or PolicySettings()
        self._rules: List[PolicyRule] = []
        self.reload_rules()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def settings(self) -> PolicySettings:
        return self._settings

    @property
    def rules(self) -> List[PolicyRule]:
        """Current sorted rule list (read-only view)."""
        return list(self._rules)

    def reload_rules(self) -> None:
        """Rebuild the rule list from built-in + global + project policies."""
        built_in = get_built_in_rules_for_mode(self._settings.approval_mode)
        self._rules = [
            *built_in,
            *self._settings.additional_global_policies,
            *self._settings.additional_project_policies,
        ]
        # Sort by priority descending — highest priority first
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def set_approval_mode(self, mode: ApprovalMode) -> None:
        """Update approval mode at runtime (e.g. user presses YOLO in UI)."""
        self._settings.approval_mode = mode
        self.reload_rules()

    def add_rule(self, rule: PolicyRule) -> None:
        """
        Add a rule at runtime (e.g. "Always Allow" for a specific tool).
        Default priority is 100 (overrides built-in rules).
        """
        if rule.priority == 0:
            rule.priority = 100
        self._settings.additional_global_policies.append(rule)
        self.reload_rules()

    def check(self, tool_name: str, args: Optional[Dict[str, Any]] = None) -> CheckResult:
        """
        Main entry point: check if a tool call is allowed.

        Iterates rules in priority order. First match wins.
        If no rule matches, fallback to ASK_USER.
        """
        args = args or {}

        for rule in self._rules:
            if self._matches_rule(rule, tool_name, args):
                return CheckResult(
                    tool=tool_name,
                    decision=rule.action,
                    matched_rule=rule,
                    reason=(
                        f"Matched rule: {rule.source or 'custom'} "
                        f"(tool={rule.tool}, priority={rule.priority})"
                    ),
                )

        # No rule matched → ask user as fallback
        return CheckResult(
            tool=tool_name,
            decision=PermissionDecision.ASK_USER,
            reason="No matching rule found",
        )

    # ------------------------------------------------------------------
    # Private matching
    # ------------------------------------------------------------------

    def _matches_rule(
        self, rule: PolicyRule, tool_name: str, args: Dict[str, Any]
    ) -> bool:
        # 1. Check tool name (supports glob: "*", "run_*", exact)
        if not self._glob_match(rule.tool, tool_name):
            return False

        # 2. Check mode filter — if rule specifies modes, current must be in list
        if rule.modes:
            if self._settings.approval_mode not in rule.modes:
                return False

        # 3. Check args — each key must glob-match
        if rule.args:
            for key, pattern in rule.args.items():
                arg_value = str(args.get(key, ""))
                if not self._glob_match(pattern, arg_value):
                    return False

        return True

    @staticmethod
    def _glob_match(pattern: str, value: str) -> bool:
        """
        Simple glob matching:  '*' matches anything, '?' matches one char.
        Uses fnmatch which handles *, ?, [seq], [!seq].
        """
        if pattern == "*":
            return True
        return fnmatch.fnmatch(value, pattern)
