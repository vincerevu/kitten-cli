"""
Path utilities.
Ref: gemini-cli/packages/core/src/utils/paths.ts
"""
import os
import platform
from typing import Optional


def normalize_path(path: str) -> str:
    """Normalize a file path for cross-platform consistency."""
    path = os.path.normpath(path)
    if platform.system() == "Windows":
        path = path.replace("\\", "/")
    return path


def make_relative(path: str, base: Optional[str] = None) -> str:
    """Make a path relative to a base directory."""
    if base is None:
        base = os.getcwd()
    try:
        return os.path.relpath(path, base)
    except ValueError:
        # On Windows, paths on different drives can't be made relative
        return path


def ensure_dir(path: str) -> str:
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(path, exist_ok=True)
    return path


def is_subpath(child: str, parent: str) -> bool:
    """Check if child path is inside parent path."""
    child = os.path.abspath(child)
    parent = os.path.abspath(parent)
    return child.startswith(parent + os.sep) or child == parent


def get_home_dir() -> str:
    """Get the user's home directory."""
    return os.path.expanduser("~")


def get_kitten_dir() -> str:
    """Get the kitten-cli config directory (~/.kitten)."""
    return os.path.join(get_home_dir(), ".kitten")


def get_kitten_history_dir() -> str:
    """Get the kitten-cli history directory (~/.kitten/history)."""
    return ensure_dir(os.path.join(get_kitten_dir(), "history"))


def get_kitten_policies_dir() -> str:
    """Get the kitten-cli policies directory (~/.kitten/policies)."""
    return ensure_dir(os.path.join(get_kitten_dir(), "policies"))


def shorten_path(path: str, max_len: int = 60) -> str:
    """Shorten a long path for display."""
    if len(path) <= max_len:
        return path
    parts = path.split(os.sep)
    if len(parts) <= 3:
        return path
    return os.sep.join([parts[0], "...", *parts[-2:]])
