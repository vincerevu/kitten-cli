
import os
from typing import Any, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult

MEMORY_FILENAME = "KITTEN.md"


class MemoryTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="memory",
            display_name="Memory",
            description=(
                "Read or write the KITTEN.md memory file. "
                "Use 'read' to load saved context, or 'write' to save important information."
            ),
            kind=ToolKind.MEMORY,
            parameter_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["read", "write"],
                        "description": "Action: 'read' or 'write'.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (only for 'write' action).",
                    },
                },
                "required": ["action"],
            },
        )
        self._workspace_root: str = os.getcwd()

    def set_workspace_root(self, path: str) -> None:
        self._workspace_root = path

    async def execute(
        self,
        action: str,
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> ToolResult:
        memory_path = os.path.join(self._workspace_root, MEMORY_FILENAME)

        if action == "read":
            if not os.path.exists(memory_path):
                return ToolResult(llm_content="No KITTEN.md memory file found.")
            try:
                with open(memory_path, "r", encoding="utf-8") as f:
                    text = f.read()
                return ToolResult(
                    llm_content=f"Memory from {MEMORY_FILENAME}:\n\n{text}"
                )
            except Exception as ex:
                return ToolResult(
                    llm_content=f"Error reading memory: {ex}",
                    error={"message": str(ex)},
                )

        elif action == "write":
            if not content:
                return ToolResult(
                    llm_content="Error: content is required for write action.",
                    error={"message": "content required"},
                )
            try:
                with open(memory_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return ToolResult(
                    llm_content=f"Saved memory to {MEMORY_FILENAME}"
                )
            except Exception as ex:
                return ToolResult(
                    llm_content=f"Error writing memory: {ex}",
                    error={"message": str(ex)},
                )
        else:
            return ToolResult(
                llm_content=f"Error: Unknown action '{action}'. Use 'read' or 'write'.",
                error={"message": f"Unknown action: {action}"},
            )
