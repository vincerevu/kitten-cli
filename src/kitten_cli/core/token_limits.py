
# Token limits for popular models
MODEL_TOKEN_LIMITS = {
    # Gemini
    "gemini-2.5-pro": 1_048_576,
    "gemini-2.5-flash": 1_048_576,
    "gemini-2.0-flash": 1_048_576,
    "gemini-1.5-pro": 2_097_152,
    "gemini-1.5-flash": 1_048_576,
    # OpenAI
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-4-turbo": 128_000,
    "gpt-4": 8_192,
    "o1": 200_000,
    "o1-mini": 128_000,
    "o3": 200_000,
    "o3-mini": 200_000,
    "o4-mini": 200_000,
    # Claude
    "claude-sonnet-4-20250514": 200_000,
    "claude-opus-4-20250514": 200_000,
    "claude-3-5-sonnet": 200_000,
    "claude-3-haiku": 200_000,
    # Default
    "default": 128_000,
}

# Reserve tokens for system prompt and response
SYSTEM_PROMPT_RESERVE = 8_000
RESPONSE_RESERVE = 8_192


def get_context_window(model: str) -> int:
    """Get the context window size for a model."""
    # Try exact match
    if model in MODEL_TOKEN_LIMITS:
        return MODEL_TOKEN_LIMITS[model]
    # Try prefix match
    for key, limit in MODEL_TOKEN_LIMITS.items():
        if model.startswith(key):
            return limit
    return MODEL_TOKEN_LIMITS["default"]


def get_available_tokens(model: str) -> int:
    """Get available tokens after reserves."""
    total = get_context_window(model)
    return total - SYSTEM_PROMPT_RESERVE - RESPONSE_RESERVE


def should_compress(current_tokens: int, model: str, threshold: float = 0.8) -> bool:
    """Check if context should be compressed (exceeds threshold)."""
    total = get_context_window(model)
    return current_tokens > total * threshold
