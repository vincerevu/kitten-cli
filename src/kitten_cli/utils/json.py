"""
JSON utilities — safe serialization.
Ref: gemini-cli/packages/core/src/utils/safeJsonStringify.ts
"""
import json
from typing import Any


def safe_json_dumps(obj: Any, indent: int = 2, max_length: int = 50000) -> str:
    """Safely serialize an object to JSON string, handling circular refs and long output."""
    try:
        text = json.dumps(obj, indent=indent, default=str, ensure_ascii=False)
        if len(text) > max_length:
            text = text[:max_length] + f"\n... [truncated, {len(text)} total chars]"
        return text
    except (TypeError, ValueError) as ex:
        return f"<unserializable: {ex}>"


def safe_json_loads(text: str) -> Any:
    """Safely parse JSON, returning None on failure."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
