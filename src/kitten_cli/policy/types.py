

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Permission decision for a tool call
# ---------------------------------------------------------------------------

class PermissionDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK_USER = "ask-user"


# ---------------------------------------------------------------------------
# Approval modes — ordered from most restrictive → most permissive
# ---------------------------------------------------------------------------

class ApprovalMode(str, Enum):
    PLAN = "plan"
    DEFAULT = "default"
    AUTO_EDIT = "autoEdit"
    FULL_AUTO = "fullAuto"
    YOLO = "yolo"


# Ordered from most restrictive to least restrictive
MODES_BY_PERMISSIVENESS: List[ApprovalMode] = [
    ApprovalMode.PLAN,
    ApprovalMode.DEFAULT,
    ApprovalMode.AUTO_EDIT,
    ApprovalMode.FULL_AUTO,
    ApprovalMode.YOLO,
]


# ---------------------------------------------------------------------------
# Tool name classification sets
# ---------------------------------------------------------------------------

# Tools that modify files
EDIT_TOOL_NAMES: Set[str] = {
    "write_file", "edit_file",                                          # kitten-cli
    "write_to_file", "replace_file_content", "multi_replace_file_content",  # gemini-cli compat
}

# Tools that run shell commands
COMMAND_TOOL_NAMES: Set[str] = {"run_command"}

# Read-only tools
READ_TOOL_NAMES: Set[str] = {
    "read_file", "read_many_files",
    "list_directory",
    "grep", "glob",
    "web_fetch", "web_search",
}

# Informational tools (never need confirmation)
INFO_TOOL_NAMES: Set[str] = {
    "ask_user", "complete_task", "memory",
}


# ---------------------------------------------------------------------------
# PolicyRule
# ---------------------------------------------------------------------------

@dataclass
class PolicyRule:
    """A single policy rule for tool approval."""

    # Glob pattern matching tool name ("*", "run_command", "write_*")
    tool: str = "*"

    # What to do when matched
    action: PermissionDecision = PermissionDecision.ASK_USER

    # Optional: only match when args satisfy this key→glob mapping
    args: Optional[Dict[str, str]] = None

    # Optional: only apply in specific approval modes
    modes: Optional[List[ApprovalMode]] = None

    # Priority: higher wins, default 0
    priority: int = 0

    # Source label for debugging (e.g. "built-in:default", "global:mypolicy.toml")
    source: str = ""


# ---------------------------------------------------------------------------
# CheckResult
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Result of evaluating a tool call against policy rules."""

    tool: str
    decision: PermissionDecision
    matched_rule: Optional[PolicyRule] = None
    reason: str = ""


# ---------------------------------------------------------------------------
# PolicySettings
# ---------------------------------------------------------------------------

@dataclass
class PolicySettings:
    """Configuration for the policy engine."""

    approval_mode: ApprovalMode = ApprovalMode.DEFAULT
    additional_global_policies: List[PolicyRule] = field(default_factory=list)
    additional_project_policies: List[PolicyRule] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Built-in rules per mode (ref: getBuiltInRulesForMode in types.ts)
# ---------------------------------------------------------------------------

def get_built_in_rules_for_mode(mode: ApprovalMode) -> List[PolicyRule]:
    """
    Return the default policy rules for the given approval mode.
    
    Priority layout:
      -100  = wildcard fallback (allow-all base)
       -90  = mode-specific restrictions (deny/ask for certain tool sets)
    """

    if mode == ApprovalMode.YOLO:
        return [
            PolicyRule(tool="*", action=PermissionDecision.ALLOW, priority=-100, source="built-in:yolo"),
        ]

    if mode == ApprovalMode.FULL_AUTO:
        return [
            PolicyRule(tool="*", action=PermissionDecision.ALLOW, priority=-100, source="built-in:fullAuto"),
        ]

    if mode == ApprovalMode.PLAN:
        rules = [
            PolicyRule(tool="*", action=PermissionDecision.ALLOW, priority=-100, source="built-in:plan"),
        ]
        for t in EDIT_TOOL_NAMES:
            rules.append(PolicyRule(tool=t, action=PermissionDecision.DENY, priority=-90, source="built-in:plan"))
        for t in COMMAND_TOOL_NAMES:
            rules.append(PolicyRule(tool=t, action=PermissionDecision.DENY, priority=-90, source="built-in:plan"))
        return rules

    if mode == ApprovalMode.AUTO_EDIT:
        rules = [
            PolicyRule(tool="*", action=PermissionDecision.ALLOW, priority=-100, source="built-in:autoEdit"),
        ]
        for t in COMMAND_TOOL_NAMES:
            rules.append(PolicyRule(tool=t, action=PermissionDecision.ASK_USER, priority=-90, source="built-in:autoEdit"))
        return rules

    # DEFAULT mode
    rules = [
        PolicyRule(tool="*", action=PermissionDecision.ALLOW, priority=-100, source="built-in:default"),
    ]
    for t in EDIT_TOOL_NAMES:
        rules.append(PolicyRule(tool=t, action=PermissionDecision.ASK_USER, priority=-90, source="built-in:default"))
    for t in COMMAND_TOOL_NAMES:
        rules.append(PolicyRule(tool=t, action=PermissionDecision.ASK_USER, priority=-90, source="built-in:default"))
    return rules
