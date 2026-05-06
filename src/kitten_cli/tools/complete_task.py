"""
CompleteTaskTool — Signal task completion to the agent loop.
Ref: gemini-cli/packages/core/src/tools/complete-task.ts
"""
from typing import Any
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class CompleteTaskTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="complete_task",
            display_name="Complete Task",
            description="Signal that the current task is complete. Provide a summary of what was accomplished.",
            kind=ToolKind.INFO,
            parameter_schema={
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Summary of what was accomplished.",
                    },
                },
                "required": ["summary"],
            },
        )

    async def execute(
        self,
        summary: str,
        **kwargs: Any,
    ) -> ToolResult:
        return ToolResult(
            llm_content=f"Task completed: {summary}",
            data={"completed": True, "summary": summary},
        )
