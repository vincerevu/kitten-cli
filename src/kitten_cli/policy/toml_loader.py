
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from kitten_cli.policy.types import (
    ApprovalMode,
    PermissionDecision,
    PolicyRule,
)

# Python 3.11+ has tomllib in stdlib
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib  # type: ignore[import]
    except ImportError:
        import tomli as tomllib  # type: ignore[import,no-redef]


# ---------------------------------------------------------------------------
# Default policy directories
# ---------------------------------------------------------------------------

def _global_policy_dir() -> Path:
    """~/.kitten/policies/"""
    return Path.home() / ".kitten" / "policies"


def _project_policy_dir(workspace_root: str) -> Path:
    """<workspace>/.kitten/policies/"""
    return Path(workspace_root) / ".kitten" / "policies"


# ---------------------------------------------------------------------------
# Parse helpers
# ---------------------------------------------------------------------------

def _parse_action(raw: str) -> PermissionDecision:
    """Parse action string → PermissionDecision enum."""
    mapping = {
        "allow": PermissionDecision.ALLOW,
        "deny": PermissionDecision.DENY,
        "ask": PermissionDecision.ASK_USER,
        "ask-user": PermissionDecision.ASK_USER,
        "ask_user": PermissionDecision.ASK_USER,
    }
    result = mapping.get(raw.lower())
    if result is None:
        raise ValueError(
            f"Invalid policy action '{raw}'. Must be one of: allow, deny, ask-user"
        )
    return result


def _parse_mode(raw: str) -> ApprovalMode:
    """Parse mode string → ApprovalMode enum."""
    try:
        return ApprovalMode(raw)
    except ValueError:
        # Try case-insensitive lookup
        for m in ApprovalMode:
            if m.value.lower() == raw.lower():
                return m
        raise ValueError(f"Invalid approval mode '{raw}'")


# ---------------------------------------------------------------------------
# Core loader
# ---------------------------------------------------------------------------

def load_policies_from_dir(dir_path: str | Path, source: str) -> List[PolicyRule]:
    """
    Load all .toml files from a directory, parse them, return PolicyRule[].

    Each TOML file should have a [[rules]] array:
        [[rules]]
        tool = "run_command"
        action = "allow"
        priority = 50
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        return []

    rules: List[PolicyRule] = []
    toml_files = sorted(dir_path.glob("*.toml"))

    for file_path in toml_files:
        try:
            with open(file_path, "rb") as f:
                parsed = tomllib.load(f)
        except Exception as err:
            print(f"Warning: Failed to parse policy file {file_path}: {err}", file=sys.stderr)
            continue

        raw_rules = parsed.get("rules", [])
        if not isinstance(raw_rules, list):
            print(f"Warning: 'rules' in {file_path} is not an array, skipping", file=sys.stderr)
            continue

        for raw in raw_rules:
            if not isinstance(raw, dict):
                continue
            try:
                rule = _parse_rule(raw, source=f"{source}:{file_path.name}")
                rules.append(rule)
            except (ValueError, KeyError) as err:
                print(
                    f"Warning: Invalid rule in {file_path}: {err}",
                    file=sys.stderr,
                )

    return rules


def _parse_rule(raw: Dict[str, Any], source: str) -> PolicyRule:
    """Parse a single raw TOML dict → PolicyRule."""

    action = _parse_action(str(raw.get("action", "ask-user")))

    # Parse optional args dict (key→glob string)
    args = raw.get("args")
    if args is not None and not isinstance(args, dict):
        raise ValueError(f"'args' must be a table/dict, got {type(args).__name__}")
    if isinstance(args, dict):
        args = {str(k): str(v) for k, v in args.items()}

    # Parse optional modes list
    modes = None
    raw_modes = raw.get("modes")
    if raw_modes is not None:
        if isinstance(raw_modes, list):
            modes = [_parse_mode(str(m)) for m in raw_modes]
        else:
            raise ValueError(f"'modes' must be a list, got {type(raw_modes).__name__}")

    return PolicyRule(
        tool=str(raw.get("tool", "*")),
        action=action,
        args=args,
        modes=modes,
        priority=int(raw.get("priority", 10)),  # user rules default to 10
        source=source,
    )


# ---------------------------------------------------------------------------
# Convenience: load global + project policies
# ---------------------------------------------------------------------------

def load_all_policies(workspace_root: str) -> Dict[str, List[PolicyRule]]:
    """
    Load global + project policies.

    Returns:
        {"global_policies": [...], "project_policies": [...]}
    """
    global_policies = load_policies_from_dir(
        _global_policy_dir(), source="global"
    )
    project_policies = load_policies_from_dir(
        _project_policy_dir(workspace_root), source="project"
    )
    return {
        "global_policies": global_policies,
        "project_policies": project_policies,
    }
