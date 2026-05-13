import json
from typing import List, Dict, Any

from litellm import acompletion

from kitten_cli.config.settings import AppConfig
from kitten_cli.context.types import DEFAULT_TAIL_TURNS, SUMMARY_TEMPLATE


async def compress_history(
    history: List[Dict[str, Any]], 
    config: AppConfig,
    tail_turns: int = DEFAULT_TAIL_TURNS
) -> List[Dict[str, Any]]:
    """
    LLM-based session compaction.
    Preserves the latest `tail_turns` turns without summarization.
    Splits history: the older part is passed to the LLM to generate or update a structured summary.
    Incorporates a self-correction probe step.
    """
    if len(history) <= tail_turns * 2 + 1:
        # Not enough history to compress
        return history

    # A "turn" typically means a user message + assistant response + tool responses
    # We will identify tail turns by counting user messages from the end
    user_msg_indices = [i for i, msg in enumerate(history) if msg.get("role") == "user"]
    
    if len(user_msg_indices) <= tail_turns:
        # Cannot preserve tail_turns and have older turns to summarize
        return history
        
    split_index = user_msg_indices[-tail_turns]
    
    system_msgs = [m for m in history[:split_index] if m.get("role") == "system"]
    older_history = [m for m in history[:split_index] if m.get("role") != "system"]
    tail_history = history[split_index:]
    
    # We construct a prompt to summarize older_history
    # If there is already a previous summary at the beginning of older_history, the LLM will see it and update it.
    history_str = json.dumps(older_history, indent=2, ensure_ascii=False)
    
    prompt = (
        f"{SUMMARY_TEMPLATE}\n\n"
        f"Here is the conversation history to summarize:\n{history_str}"
    )
    
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant tasked with summarizing conversation history for context compaction."},
        {"role": "user", "content": prompt}
    ]
    
    llm_config = config.llm
    
    try:
        response = await acompletion(
            model=llm_config.model,
            messages=messages,
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            temperature=0.3, # low temperature for more factual summary
            top_p=llm_config.top_p,
        )
        summary = response.choices[0].message.content
        
        # Self-correction probe
        correction_prompt = (
            "Review the summary above against the original history. "
            "Did you omit any critical file paths, technical constraints, or explicit user preferences? "
            "If so, output an updated summary that includes them. Otherwise, just output the exact same summary."
        )
        
        messages.append({"role": "assistant", "content": summary})
        messages.append({"role": "user", "content": correction_prompt})
        
        correction_response = await acompletion(
            model=llm_config.model,
            messages=messages,
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
            temperature=0.3,
            top_p=llm_config.top_p,
        )
        final_summary = correction_response.choices[0].message.content
        
    except Exception as ex:
        # If compression fails (e.g. network error, context length exceeded for the summarization call itself)
        # return the original history uncompressed, or fallback to dropping older history.
        print(f"Warning: Compression failed: {ex}")
        return history
        
    # Reconstruct the history
    compressed_history = system_msgs + [{"role": "system", "content": f"Previous conversation summary:\n{final_summary}"}] + tail_history
    return compressed_history
