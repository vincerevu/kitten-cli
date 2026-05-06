from typing import Any, AsyncGenerator

import litellm

from kitten_cli.config.manager import ConfigManager
from kitten_cli.agents.types import AgentEvent, AgentEventType


class KittenLLM:
    """Wrapper for LiteLLM"""
    def __init__(self):
        self.config = ConfigManager.load_config()
    async def stream(
        self,
        messages: list[dict[str,Any]],
        tools: list[dict[str,Any]] | None = None,
        errors: list[dict[str,Any]] | None = None,
        ) -> AsyncGenerator[AgentEvent,None] :
        llm_config=self.config.llm
        try:
            response = await litellm.acompletion(
                model=llm_config.model,
                messages=messages,
                api_key=llm_config.api_key,
                base_url=llm_config.base_url,
                temperature=llm_config.temperature,
                top_p=llm_config.top_p,
                max_tokens=llm_config.max_output_tokens,
                stream=True,
                tools=tools,
            )
            async for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield AgentEvent(type=AgentEventType.CONTENT, value=delta.content)
                elif delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        yield AgentEvent(type=AgentEventType.TOOL_CALL_CHUNK, value=tool_call)
        except Exception as ex:
            yield AgentEvent(type=AgentEventType.ERROR, value=ex)

