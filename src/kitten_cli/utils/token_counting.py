"""
Token counting utilities.
Ref: gemini-cli/packages/core/src/utils/tokenCalculation.ts

Provides fast approximate token counting for context window management.
Uses character-based heuristics (1 token ~ 4 chars for English text).
"""

from typing import Any, Dict, List, Optional, Union


# Approximate tokens-per-character ratio
# English: ~4 chars/token, CJK: ~1.5 chars/token, Code: ~3.5 chars/token
CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    Uses the ~4 chars/token heuristic for English.
    """
    if not text:
        return 0
    return max(1, len(text) // CHARS_PER_TOKEN)


def estimate_message_tokens(message: Dict[str, Any]) -> int:
    """
    Estimate tokens for a single LLM message.
    Accounts for role, content, and tool_calls.
    """
    tokens = 4  # Base overhead per message (role, separators)

    # Content
    content = message.get("content")
    if isinstance(content, str):
        tokens += estimate_tokens(content)
    elif isinstance(content, list):
        for part in content:
            if isinstance(part, dict):
                tokens += estimate_tokens(str(part.get("text", "")))
            elif isinstance(part, str):
                tokens += estimate_tokens(part)

    # Tool calls
    tool_calls = message.get("tool_calls", [])
    for tc in tool_calls:
        tokens += 4  # tool call overhead
        if isinstance(tc, dict):
            fn = tc.get("function", {})
            tokens += estimate_tokens(fn.get("name", ""))
            tokens += estimate_tokens(str(fn.get("arguments", "")))

    return tokens


def estimate_history_tokens(history: List[Dict[str, Any]]) -> int:
    """Estimate total tokens for an entire conversation history."""
    return sum(estimate_message_tokens(msg) for msg in history)


def check_context_limit(
    history: List[Dict[str, Any]],
    context_window: int,
    threshold: float = 0.7,
) -> Dict[str, Any]:
    """
    Check if the conversation is approaching the context limit.
    Returns a report with usage stats.
    """
    total_tokens = estimate_history_tokens(history)
    limit = int(context_window * threshold)

    return {
        "total_tokens": total_tokens,
        "context_window": context_window,
        "threshold": threshold,
        "threshold_tokens": limit,
        "usage_ratio": total_tokens / context_window if context_window > 0 else 0,
        "needs_compaction": total_tokens >= limit,
        "messages_count": len(history),
    }


def truncate_to_token_limit(text: str, max_tokens: int) -> str:
    """Truncate text to approximately max_tokens tokens."""
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... [truncated, {estimate_tokens(text)} tokens total]"
