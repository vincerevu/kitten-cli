
import uuid
from pathlib import Path
from typing import List, Dict, Any, Callable
from kitten_cli.context.types import PRUNE_PROTECT

def prune_tool_outputs(
        history: List[Dict[str, Any]], 
        count_tokens: Callable[[str], int],
        protect_tokens: int = PRUNE_PROTECT
) -> List[Dict[str, Any]]:
    """
    Scans history backwards (excluding the last turn).
    Keeps track of cumulative tool response tokens.
    Once the threshold is reached, prunes older tool outputs.
    Pruned outputs are written to ~/.kitten/tmp/tool-outputs/ and replaced with a placeholder.
    """
    
    # Do not mutate original
    new_history = list(history)
    
    # Create temp directory
    tmp_dir = Path.home() / ".kitten" / "tmp" / "tool-outputs"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    # Find the boundary of the "last turn" (e.g., from the last user message onwards)
    last_user_idx = -1
    for i in range(len(new_history) - 1, -1, -1):
        if new_history[i].get("role") == "user":
            last_user_idx = i
            break
            
    if last_user_idx == -1:
        last_user_idx = len(new_history)
        
    accumulated_tool_tokens = 0
    
    # Go backwards from just before the last user message
    for i in range(last_user_idx - 1, -1, -1):
        msg = new_history[i]
        
        if msg.get("role") == "tool":
            content = msg.get("content", "")
            if not content:
                continue
                
            content_str = str(content)
            tokens = count_tokens(content_str)
            
            if accumulated_tool_tokens + tokens > protect_tokens:
                # We need to prune this one.
                # If we are partially over, we just prune the whole thing for simplicity.
                file_id = uuid.uuid4().hex[:8]
                tool_call_id = msg.get("tool_call_id", "unknown")
                file_path = tmp_dir / f"{tool_call_id}_{file_id}.txt"
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content_str)
                    
                preview = content_str[:200] + ("..." if len(content_str) > 200 else "")
                placeholder = f"[Tool output pruned due to length. Saved to {file_path}]\nPreview: {preview}"
                
                # Replace in history
                new_msg = dict(msg)
                new_msg["content"] = placeholder
                new_history[i] = new_msg
            else:
                accumulated_tool_tokens += tokens
                
    return new_history
