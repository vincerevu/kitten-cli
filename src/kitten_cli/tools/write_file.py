"""
WriteFileTool — Create or overwrite files.
Ref: gemini-cli/packages/core/src/tools/write-file.ts
"""
import os
from typing import Any
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class WriteFileTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="write_file",
            display_name="Write File",
            description="Create a new file or overwrite an existing file with the provided content.",
            kind=ToolKind.EDIT,
            parameter_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to write.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file.",
                    },
                },
                "required": ["file_path", "content"],
            },
        )

    async def execute(
        self,
        file_path: str,
        content: str,
        **kwargs: Any,
    ) -> ToolResult:
        file_path = os.path.abspath(file_path)

        # Create parent directories if needed
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except OSError as ex:
                return ToolResult(
                    llm_content=f"Error: Could not create directory: {ex}",
                    error={"message": str(ex)},
                )

        existed = os.path.exists(file_path)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as ex:
            return ToolResult(
                llm_content=f"Error writing file: {ex}",
                error={"message": str(ex)},
            )

        line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
        action = "Updated" if existed else "Created"
        return ToolResult(
            llm_content=f"{action} file: {file_path} ({line_count} lines)"
        )
