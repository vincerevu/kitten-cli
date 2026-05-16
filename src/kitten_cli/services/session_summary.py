"""
Session summary service — generates a summary when a session ends.
Ref: gemini-cli/packages/core/src/services/sessionSummaryService.ts

Uses the LLM to create a concise summary of what was accomplished during the session.
The summary can be stored for later reference or displayed to the user.
"""

import json
from typing import Any, Dict, List, Optional

from litellm import acompletion

from kitten_cli.config.settings import AppConfig


SESSION_SUMMARY_PROMPT = """Summarize this coding session concisely. Include:
1. What was the main goal?
2. What files were created or modified?
3. What was accomplished?
4. What remains to be done (if anything)?

Keep it brief (3-5 bullet points max). Focus on concrete outcomes, not process.

Conversation history:
{history}"""


class SessionSummaryService:
    """
    Generates session summaries using the LLM when a session ends.
    Summaries are compact and focus on outcomes.
    """

    def __init__(self, config: AppConfig):
        self.config = config

    async def generate_summary(
        self,
        history: List[Dict[str, Any]],
        max_history_chars: int = 30_000,
    ) -> str:
        """
        Generate a summary of the conversation session.
        Truncates history if too long before sending to LLM.
        """
        if not history:
            return "Empty session - no activity."

        # Serialize history to string, truncating if needed
        history_str = json.dumps(history, ensure_ascii=False, indent=1)
        if len(history_str) > max_history_chars:
            history_str = history_str[:max_history_chars] + "\n... (truncated)"

        prompt = SESSION_SUMMARY_PROMPT.format(history=history_str)

        try:
            llm_config = self.config.llm
            response = await acompletion(
                model=llm_config.model,
                messages=[
                    {"role": "system", "content": "You are a concise technical summarizer."},
                    {"role": "user", "content": prompt},
                ],
                api_key=llm_config.api_key,
                base_url=llm_config.base_url,
                temperature=0.3,
                max_tokens=500,
            )
            return response.choices[0].message.content.strip()
        except Exception as ex:
            return f"(Summary generation failed: {ex})"

    @staticmethod
    def format_quick_summary(history: List[Dict[str, Any]]) -> str:
        """
        Generate a quick, offline summary without LLM.
        Counts turns, tool calls, and extracts the first user message as context.
        """
        if not history:
            return "Empty session."

        user_msgs = [m for m in history if m.get("role") == "user"]
        assistant_msgs = [m for m in history if m.get("role") == "assistant"]
        tool_msgs = [m for m in history if m.get("role") == "tool"]

        # Count tool calls from assistant messages
        tool_calls_count = sum(
            len(m.get("tool_calls", []))
            for m in assistant_msgs
        )

        # Get first user message as topic hint
        first_user = ""
        if user_msgs:
            content = user_msgs[0].get("content", "")
            if isinstance(content, str):
                first_user = content[:100] + ("..." if len(content) > 100 else "")

        lines = [
            f"Session: {len(user_msgs)} user turns, {len(assistant_msgs)} assistant turns",
            f"Tool calls: {tool_calls_count}, Tool results: {len(tool_msgs)}",
        ]
        if first_user:
            lines.append(f"Topic: {first_user}")

        return "\n".join(lines)
