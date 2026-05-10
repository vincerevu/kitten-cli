
import os
from typing import Optional, Tuple


def read_file_safe(path: str, encoding: str = "utf-8") -> Tuple[Optional[str], Optional[str]]:
    """Read a file safely, return (content, error_message)."""
    try:
        with open(path, "r", encoding=encoding, errors="replace") as f:
            return f.read(), None
    except FileNotFoundError:
        return None, f"File not found: {path}"
    except PermissionError:
        return None, f"Permission denied: {path}"
    except Exception as ex:
        return None, str(ex)


def write_file_safe(path: str, content: str, encoding: str = "utf-8") -> Optional[str]:
    """Write a file safely, return error_message or None."""
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return None
    except Exception as ex:
        return str(ex)


def is_binary_file(path: str, sample_size: int = 8192) -> bool:
    """Check if a file is binary by reading the first N bytes."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(sample_size)
        # Check for null bytes
        if b"\x00" in chunk:
            return True
        # Check ratio of non-text bytes
        text_chars = set(range(32, 127)) | {9, 10, 13}  # printable + tab, nl, cr
        non_text = sum(1 for b in chunk if b not in text_chars)
        return non_text / max(len(chunk), 1) > 0.3
    except Exception:
        return True


def file_size_str(path: str) -> str:
    """Get human-readable file size."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f}{unit}" if unit != "B" else f"{size}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def count_lines(path: str) -> int:
    """Count lines in a text file."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0
