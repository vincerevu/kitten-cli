"""
Environment context — collects runtime environment info for system prompts.
Ref: gemini-cli/packages/core/src/utils/environmentContext.ts

Provides contextual information about the user's environment:
  - OS, shell, cwd
  - Python version
  - Git branch / repo status
  - Date/time/timezone
"""

import os
import platform
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from kitten_cli.utils.shell_utils import get_shell_info


def get_environment_context(
    project_root: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Collect environment context for injection into system prompts.
    """
    cwd = project_root or os.getcwd()

    ctx = {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "cwd": cwd,
        "home": str(os.path.expanduser("~")),
        "user": os.environ.get("USER") or os.environ.get("USERNAME", "unknown"),
        "shell": get_shell_info().get("shell_path", "unknown"),
        "datetime": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "timezone": datetime.now().astimezone().strftime("%Z"),
    }

    return ctx


def format_environment_context(ctx: Optional[Dict[str, Any]] = None) -> str:
    """Format environment context as a string for system prompts."""
    if ctx is None:
        ctx = get_environment_context()

    lines = [
        f"OS: {ctx.get('os', 'unknown')} ({ctx.get('architecture', 'unknown')})",
        f"Shell: {ctx.get('shell', 'unknown')}",
        f"Python: {ctx.get('python_version', 'unknown')}",
        f"CWD: {ctx.get('cwd', 'unknown')}",
        f"Date: {ctx.get('datetime', 'unknown')}",
    ]

    return "\n".join(lines)
