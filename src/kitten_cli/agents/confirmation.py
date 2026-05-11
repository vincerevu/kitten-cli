"""
agents/confirmation.py — Bridge between old check_policy() API and new PolicyEngine.

Maintains backward compatibility: check_policy(tool_name, args, config) → PolicyDecision
Now delegates to policy.engine.PolicyEngine internally.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict

from kitten_cli.config.settings import AppConfig
from kitten_cli.config.settings import ApprovalMode as ConfigApprovalMode
from kitten_cli.policy.types import (
    ApprovalMode as PolicyApprovalMode,
    PermissionDecision,
    PolicySettings,
)
from kitten_cli.policy.engine import PolicyEngine


# Re-export for backward compat
class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK_USER = "ask_user"


# Map ConfigApprovalMode → PolicyApprovalMode
_MODE_MAP = {
    ConfigApprovalMode.DEFAULT: PolicyApprovalMode.DEFAULT,
    ConfigApprovalMode.AUTO_EDIT: PolicyApprovalMode.AUTO_EDIT,
    ConfigApprovalMode.YOLO: PolicyApprovalMode.YOLO,
    ConfigApprovalMode.PLAN: PolicyApprovalMode.PLAN,
}

# Map PermissionDecision → PolicyDecision
_DECISION_MAP = {
    PermissionDecision.ALLOW: PolicyDecision.ALLOW,
    PermissionDecision.DENY: PolicyDecision.DENY,
    PermissionDecision.ASK_USER: PolicyDecision.ASK_USER,
}


def check_policy(tool_name: str, args: Dict[str, Any], config: AppConfig) -> PolicyDecision:
    """
    Check if a tool execution is allowed based on the current ApprovalMode.

    Delegates to PolicyEngine for full rule matching.
    """
    policy_mode = _MODE_MAP.get(config.approval_mode, PolicyApprovalMode.DEFAULT)
    engine = PolicyEngine(PolicySettings(approval_mode=policy_mode))
    result = engine.check(tool_name, args)
    return _DECISION_MAP.get(result.decision, PolicyDecision.ASK_USER)
