"""
String and tool output truncation algorithms.
"""

def truncate_proportionally(text: str, target_chars: int, prefix: str = "", head_ratio: float = 0.2) -> str:
    """
    Truncate a string proportionally, keeping head and tail chunks separated by an ellipsis placeholder.
    """
    if len(text) <= target_chars:
        return text

    head_chars = int(target_chars * head_ratio)
    tail_chars = target_chars - head_chars
    
    ellipsis = f"\n... {prefix} (truncated) ...\n"
    
    head_text = text[:head_chars]
    tail_text = text[-tail_chars:] if tail_chars > 0 else ""
    
    return f"{head_text}{ellipsis}{tail_text}"

def normalize_function_response(result: str, max_chars: int = 50_000, head_ratio: float = 0.2) -> str:
    """
    Decodes and limits large text blobs in tool responses (like stdout/stderr).
    Defaults to 50k characters which roughly equates to 10k-12k tokens depending on the content.
    """
    if not isinstance(result, str):
        result = str(result)
        
    if len(result) > max_chars:
        return truncate_proportionally(
            text=result,
            target_chars=max_chars,
            prefix="Output too long",
            head_ratio=head_ratio
        )
    return result
