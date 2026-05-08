
import os
from typing import Any, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class LSTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="list_directory",
            display_name="List Directory",
            description="List the contents of a directory. Returns file names, sizes, and types.",
            kind=ToolKind.READ,
            parameter_schema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Absolute path to the directory to list.",
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth for recursive listing. Default 1 (non-recursive).",
                    },
                },
                "required": ["directory_path"],
            },
        )

    async def execute(
        self,
        directory_path: str,
        max_depth: int = 1,
        **kwargs: Any,
    ) -> ToolResult:
        directory_path = os.path.abspath(directory_path)

        if not os.path.exists(directory_path):
            return ToolResult(
                llm_content=f"Error: Directory not found: {directory_path}",
                error={"message": f"Directory not found: {directory_path}"},
            )

        if not os.path.isdir(directory_path):
            return ToolResult(
                llm_content=f"Error: Path is not a directory: {directory_path}",
                error={"message": "Path is not a directory"},
            )

        entries = []
        try:
            self._list_recursive(directory_path, entries, current_depth=0, max_depth=max_depth)
        except PermissionError as ex:
            return ToolResult(
                llm_content=f"Error: Permission denied: {ex}",
                error={"message": str(ex)},
            )

        header = f"Directory: {directory_path}\n"
        if not entries:
            return ToolResult(llm_content=header + "(empty directory)")

        return ToolResult(llm_content=header + "\n".join(entries))

    def _list_recursive(
        self,
        path: str,
        entries: list,
        current_depth: int,
        max_depth: int,
        prefix: str = "",
    ) -> None:
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            entries.append(f"{prefix}[permission denied]")
            return

        for item in items:
            full_path = os.path.join(path, item)
            is_dir = os.path.isdir(full_path)

            if is_dir:
                entries.append(f"{prefix}{item}/")
                if current_depth + 1 < max_depth:
                    self._list_recursive(
                        full_path, entries, current_depth + 1, max_depth, prefix + "  "
                    )
            else:
                try:
                    size = os.path.getsize(full_path)
                    entries.append(f"{prefix}{item} ({self._format_size(size)})")
                except OSError:
                    entries.append(f"{prefix}{item}")

    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f}{unit}" if unit == "B" else f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
