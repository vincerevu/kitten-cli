"""
EditTool — Edit existing files with search-and-replace.
Ref: gemini-cli/packages/core/src/tools/edit.ts (43KB — simplified core logic)
"""
import os
import difflib
from typing import Any, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class EditTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="edit_file",
            display_name="Edit File",
            description=(
                "Edit an existing file by replacing a target string with new content. "
                "The target_content must exactly match text in the file. "
                "Optionally narrow the search using start_line and end_line."
            ),
            kind=ToolKind.EDIT,
            parameter_schema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to edit.",
                    },
                    "target_content": {
                        "type": "string",
                        "description": "The exact string to find and replace. Must match exactly.",
                    },
                    "replacement_content": {
                        "type": "string",
                        "description": "The new content to replace the target with.",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Optional 1-indexed start line to narrow search scope.",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Optional 1-indexed end line to narrow search scope.",
                    },
                    "allow_multiple": {
                        "type": "boolean",
                        "description": "If true, replace all occurrences. Default false.",
                    },
                },
                "required": ["file_path", "target_content", "replacement_content"],
            },
        )

    async def execute(
        self,
        file_path: str,
        target_content: str,
        replacement_content: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        allow_multiple: bool = False,
        **kwargs: Any,
    ) -> ToolResult:
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            return ToolResult(
                llm_content=f"Error: File not found: {file_path}",
                error={"message": f"File not found: {file_path}", "type": "file_not_found"},
            )

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                original_content = f.read()
                original_lines = original_content.split("\n")
        except Exception as ex:
            return ToolResult(
                llm_content=f"Error reading file: {ex}",
                error={"message": str(ex)},
            )

        # Narrow search scope if line range provided
        if start_line is not None or end_line is not None:
            s = max(0, (start_line or 1) - 1)
            e = min(len(original_lines), end_line or len(original_lines))
            scope_text = "\n".join(original_lines[s:e])
        else:
            scope_text = original_content
            s = 0
            e = len(original_lines)

        # Count occurrences
        count = scope_text.count(target_content)

        if count == 0:
            return ToolResult(
                llm_content=f"Error: Target content not found in {file_path}" + 
                           (f" (lines {s+1}-{e})" if start_line else ""),
                error={"message": "Target content not found"},
            )

        if count > 1 and not allow_multiple:
            return ToolResult(
                llm_content=(
                    f"Error: Found {count} occurrences of target content in {file_path}. "
                    f"Use allow_multiple=true or narrow with start_line/end_line."
                ),
                error={"message": f"Multiple occurrences ({count}) found"},
            )

        # Perform replacement
        if start_line is not None or end_line is not None:
            new_scope = scope_text.replace(target_content, replacement_content)
            new_lines = original_lines[:s] + new_scope.split("\n") + original_lines[e:]
            new_content = "\n".join(new_lines)
        else:
            if allow_multiple:
                new_content = original_content.replace(target_content, replacement_content)
            else:
                new_content = original_content.replace(target_content, replacement_content, 1)

        # Write back
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as ex:
            return ToolResult(
                llm_content=f"Error writing file: {ex}",
                error={"message": str(ex)},
            )

        # Generate diff
        diff = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{os.path.basename(file_path)}",
            tofile=f"b/{os.path.basename(file_path)}",
            n=3,
        )
        diff_text = "".join(diff)

        replaced_count = count if allow_multiple else 1
        return ToolResult(
            llm_content=f"Edited {file_path} ({replaced_count} replacement{'s' if replaced_count > 1 else ''})\n\n{diff_text}",
        )
