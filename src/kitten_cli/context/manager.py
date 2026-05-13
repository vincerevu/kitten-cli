import logging
from typing import List, Dict, Any

import litellm

from kitten_cli.config.settings import AppConfig
from kitten_cli.context.types import COMPRESSION_THRESHOLD_RATIO, PRUNE_PROTECT
from kitten_cli.context.truncation import normalize_function_response
from kitten_cli.context.pruning import prune_tool_outputs
from kitten_cli.context.compression import compress_history


logger = logging.getLogger(__name__)


class ContextManager:
    """Orchestrates the entire context management flow."""
    def __init__(self, config: AppConfig):
        self.config = config

    def count_tokens(self, text: str) -> int:
        """Count tokens for a given string using litellm."""
        try:
            return litellm.token_counter(model=self.config.llm.model, text=text)
        except Exception:
            return len(str(text)) // 4

    def count_history_tokens(self, history: List[Dict[str, Any]]) -> int:
        """Count total tokens in the history."""
        try:
            return litellm.token_counter(model=self.config.llm.model, messages=history)
        except Exception:
            return sum(self.count_tokens(str(m.get("content", ""))) for m in history)

    async def manage_context(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Manages the conversation history to prevent context overflow.
        1. Truncates massive single messages/tool outputs.
        2. Prunes old tool outputs if they exceed the protect threshold.
        3. Compresses older history via LLM if total tokens exceed the context threshold.
        """
        # 1. Truncate single massive parts
        new_history = []
        for msg in history:
            new_msg = dict(msg)
            if new_msg.get("role") == "tool":
                new_msg["content"] = normalize_function_response(new_msg.get("content", ""))
            new_history.append(new_msg)

        # 2. Prune old tool outputs
        new_history = prune_tool_outputs(
            history=new_history, 
            count_tokens=self.count_tokens, 
            protect_tokens=PRUNE_PROTECT
        )

        # 3. Compression
        try:
            model_info = litellm.get_model_info(self.config.llm.model)
            context_window = model_info.get("max_tokens", 128_000)
        except Exception:
            context_window = 128_000

        current_tokens = self.count_history_tokens(new_history)
        
        if current_tokens > context_window * COMPRESSION_THRESHOLD_RATIO:
            logger.info(f"Context window at {current_tokens} tokens. Triggering compression.")
            new_history = await compress_history(new_history, self.config)

        return new_history
