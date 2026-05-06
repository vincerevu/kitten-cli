"""
GlobTool — Find files matching glob patterns.
Ref: gemini-cli/packages/core/src/tools/glob.ts
"""
import os
import glob as glob_module
from typing import Any, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class GlobTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="glob",
            display_name="Find Files",
            description="Find files matching a glob pattern (e.g. '**/*.py'). Returns matching file paths.",
            kind=ToolKind.READ,
            parameter_schema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to match (e.g. '**/*.py', 'src/**/*.ts').",
                    },
                    "path": {
                        "type": "string",
                        "description": "Base directory to search from.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results. Default 100.",
                    },
                },
                "required": ["pattern"],
            },
        )

    async def execute(
        self,
        pattern: str,
        path: Optional[str] = None,
        max_results: int = 100,
        **kwargs: Any,
    ) -> ToolResult:
        base = os.path.abspath(path) if path else os.getcwd()

        if not os.path.isdir(base):
            return ToolResult(
                llm_content=f"Error: Directory not found: {base}",
                error={"message": f"Directory not found: {base}"},
            )

        full_pattern = os.path.join(base, pattern)
        matches = glob_module.glob(full_pattern, recursive=True)

        # Filter out directories, sort, limit
        matches = sorted([m for m in matches if os.path.isfile(m)])[:max_results]

        if not matches:
            return ToolResult(llm_content=f"No files matching '{pattern}' found in {base}")

        return ToolResult(
            llm_content=f"Found {len(matches)} files:\n" + "\n".join(matches)
        )
