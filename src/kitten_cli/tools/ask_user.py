"""
AskUserTool — Ask the user a question and wait for response.
Ref: gemini-cli/packages/core/src/tools/ask-user.ts
"""
from typing import Any, Dict, List, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class AskUserTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="ask_user",
            display_name="Ask User",
            description=(
                "Ask the user a question when you need clarification or input. "
                "The user will see the question and can type a response."
            ),
            kind=ToolKind.INFO,
            parameter_schema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the user.",
                    },
                },
                "required": ["question"],
            },
        )
        # Callback set by UI to handle user interaction
        self._ask_callback = None

    def set_callback(self, callback) -> None:
        """Set the callback that handles asking the user."""
        self._ask_callback = callback

    async def execute(
        self,
        question: str,
        **kwargs: Any,
    ) -> ToolResult:
        if self._ask_callback:
            try:
                answer = await self._ask_callback(question)
                return ToolResult(
                    llm_content=f"User response: {answer}"
                )
            except Exception as ex:
                return ToolResult(
                    llm_content=f"User cancelled or error: {ex}",
                    error={"message": str(ex)},
                )
        else:
            return ToolResult(
                llm_content="Error: No UI callback configured for ask_user.",
                error={"message": "No UI callback configured"},
            )
