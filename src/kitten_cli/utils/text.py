
from typing import Optional


def truncate_text(text: str, max_length: int = 10000, suffix: str = "...") -> str:
    """Truncate text to max_length, appending suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def truncate_lines(text: str, max_lines: int = 200) -> str:
    """Truncate text by number of lines."""
    lines = text.split("\n")
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + f"\n... [{len(lines) - max_lines} more lines]"


def count_tokens_estimate(text: str) -> int:
    """
    Rough token count estimate. ~4 chars per token for English.
    For more accurate counting, use tiktoken.
    """
    return max(1, len(text) // 4)


def extract_code_blocks(text: str) -> list:
    """Extract fenced code blocks from markdown text."""
    import re
    pattern = r'```(\w*)\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [{"language": lang or "text", "code": code.strip()} for lang, code in matches]


def indent(text: str, prefix: str = "  ") -> str:
    """Add prefix to each line of text."""
    return "\n".join(prefix + line for line in text.split("\n"))
