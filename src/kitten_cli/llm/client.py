import litellm
import os
from typing import AsyncGenerator, List, Dict, Any
from kitten_cli.config.manager import ConfigManager

class KittenLLM:
    """Wrapper for LiteLLM to handle API communication using the user's config."""
    
    def __init__(self):
        self.config = ConfigManager.load_config()
        # Optionally set litellm callbacks or logging here

    async def stream_chat(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Streams a chat completion from the configured LLM provider.
        """
        llm_config = self.config.llm
        
        # Determine API key
        api_key = llm_config.api_key
        if not api_key:
            # Fallback to check if it's stored in env variables based on the model prefix
            # E.g., if model is "openai/gpt-4o", litellm will look for OPENAI_API_KEY automatically
            pass

        try:
            response = await litellm.acompletion(
                model=llm_config.model,
                messages=messages,
                api_key=api_key,
                base_url=llm_config.base_url,
                temperature=llm_config.temperature,
                top_p=llm_config.top_p,
                max_tokens=llm_config.max_output_tokens,
                stream=True
            )
            
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    
        except Exception as e:
            yield f"\n[LLM Connection Error]: {str(e)}"
