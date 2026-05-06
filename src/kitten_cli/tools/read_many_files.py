"""
ReadManyFilesTool — Read multiple files in a single call.
Ref: gemini-cli/packages/core/src/tools/read-many-files.ts
"""
import os
from typing import Any, List
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class ReadManyFilesTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="read_many_files",
            display_name="Read Many Files",
            description="Read multiple files in a single call. Provide a list of file paths.",
            kind=ToolKind.READ,
            parameter_schema={
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of absolute file paths to read.",
                    },
                },
                "required": ["file_paths"],
            },
        )

    async def execute(
        self,
        file_paths: List[str],
        **kwargs: Any,
    ) -> ToolResult:
        results = []
        errors = []

        for fp in file_paths:
            fp = os.path.abspath(fp)
            if not os.path.exists(fp):
                errors.append(f"[NOT FOUND] {fp}")
                continue
            if os.path.isdir(fp):
                errors.append(f"[IS DIR] {fp}")
                continue
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                line_count = content.count("\n") + 1
                results.append(
                    f"--- {fp} ({line_count} lines) ---\n{content}"
                )
            except Exception as ex:
                errors.append(f"[ERROR] {fp}: {ex}")

        parts = []
        if results:
            parts.append("\n\n".join(results))
        if errors:
            parts.append("Errors:\n" + "\n".join(errors))

        return ToolResult(
            llm_content="\n\n".join(parts) if parts else "No files provided.",
            error={"message": f"{len(errors)} file(s) failed"} if errors and not results else None,
        )
