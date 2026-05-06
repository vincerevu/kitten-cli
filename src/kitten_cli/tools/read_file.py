"""
ReadFileTool — Read file contents with line range support.
Ref: gemini-cli/packages/core/src/tools/read-file.ts
"""
import os
from typing import Any, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class ReadFileTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="read_file",
            display_name="Read File",
            description="Read the contents of a file. Optionally specify start_line and end_line to read a range.",
            kind=ToolKind.READ,
            parameter_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The absolute path to the file to read.",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Optional 1-indexed start line.",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Optional 1-indexed end line (inclusive).",
                    },
                },
                "required": ["file_path"],
            },
        )

    async def execute(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        **kwargs: Any,
    ) -> ToolResult:
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            return ToolResult(
                llm_content=f"Error: File not found: {file_path}",
                error={"message": f"File not found: {file_path}", "type": "file_not_found"},
            )

        if os.path.isdir(file_path):
            return ToolResult(
                llm_content=f"Error: Path is a directory, not a file: {file_path}",
                error={"message": "Path is a directory"},
            )

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception as ex:
            return ToolResult(
                llm_content=f"Error reading file: {ex}",
                error={"message": str(ex)},
            )

        total_lines = len(lines)

        # Apply line range
        if start_line is not None or end_line is not None:
            s = max(1, start_line or 1) - 1
            e = min(total_lines, end_line or total_lines)
            selected = lines[s:e]
            header = f"File: {file_path} (lines {s+1}-{e} of {total_lines})\n"
        else:
            selected = lines
            header = f"File: {file_path} ({total_lines} lines)\n"

        # Add line numbers
        numbered = []
        offset = (start_line or 1)
        for i, line in enumerate(selected):
            numbered.append(f"{offset + i}: {line.rstrip()}")

        content = header + "\n".join(numbered)
        return ToolResult(llm_content=content)
