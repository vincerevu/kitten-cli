"""
Diff generation utilities.
Ref: gemini-cli/packages/core/src/utils/fileDiffUtils.ts
"""
import difflib
from typing import Optional


def generate_unified_diff(
    original: str,
    modified: str,
    filename: str = "file",
    context_lines: int = 3,
) -> str:
    """Generate a unified diff between two strings."""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=context_lines,
    )
    return "".join(diff)


def generate_diff_stat(original: str, modified: str) -> dict:
    """Calculate diff statistics (additions, deletions)."""
    orig_lines = original.splitlines()
    mod_lines = modified.splitlines()
    diff = list(difflib.unified_diff(orig_lines, mod_lines, n=0))

    additions = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

    return {
        "additions": additions,
        "deletions": deletions,
        "total_changes": additions + deletions,
    }


def colorize_diff(diff_text: str) -> str:
    """Add ANSI colors to diff text for terminal display."""
    lines = []
    for line in diff_text.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(f"\033[32m{line}\033[0m")  # green
        elif line.startswith("-") and not line.startswith("---"):
            lines.append(f"\033[31m{line}\033[0m")  # red
        elif line.startswith("@@"):
            lines.append(f"\033[36m{line}\033[0m")  # cyan
        else:
            lines.append(line)
    return "\n".join(lines)
