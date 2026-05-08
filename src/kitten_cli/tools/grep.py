
import os
import re
import subprocess
from typing import Any, List, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class GrepTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="grep",
            display_name="Search Files",
            description="Search for a pattern in files. Supports regex. Returns matching lines with file paths and line numbers.",
            kind=ToolKind.READ,
            parameter_schema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The search pattern (regex).",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory or file path to search in.",
                    },
                    "include": {
                        "type": "string",
                        "description": "Glob pattern to filter files (e.g. '*.py').",
                    },
                    "case_insensitive": {
                        "type": "boolean",
                        "description": "Case-insensitive search. Default false.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results. Default 50.",
                    },
                },
                "required": ["pattern", "path"],
            },
        )

    async def execute(
        self,
        pattern: str,
        path: str,
        include: Optional[str] = None,
        case_insensitive: bool = False,
        max_results: int = 50,
        **kwargs: Any,
    ) -> ToolResult:
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return ToolResult(
                llm_content=f"Error: Path not found: {path}",
                error={"message": f"Path not found: {path}"},
            )

        # Try ripgrep first, fall back to Python regex
        try:
            return await self._ripgrep_search(
                pattern, path, include, case_insensitive, max_results
            )
        except FileNotFoundError:
            return self._python_search(
                pattern, path, include, case_insensitive, max_results
            )

    async def _ripgrep_search(
        self,
        pattern: str,
        path: str,
        include: Optional[str],
        case_insensitive: bool,
        max_results: int,
    ) -> ToolResult:
        cmd = ["rg", "--line-number", "--no-heading", f"--max-count={max_results}"]
        if case_insensitive:
            cmd.append("--ignore-case")
        if include:
            cmd.extend(["--glob", include])
        cmd.extend([pattern, path])

        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )

        if proc.returncode == 0 and proc.stdout.strip():
            lines = proc.stdout.strip().split("\n")[:max_results]
            return ToolResult(
                llm_content=f"Found {len(lines)} matches:\n" + "\n".join(lines)
            )
        elif proc.returncode == 1:
            return ToolResult(llm_content="No matches found.")
        else:
            raise FileNotFoundError("ripgrep not available")

    def _python_search(
        self,
        pattern: str,
        path: str,
        include: Optional[str],
        case_insensitive: bool,
        max_results: int,
    ) -> ToolResult:
        flags = re.IGNORECASE if case_insensitive else 0
        try:
            regex = re.compile(pattern, flags)
        except re.error as ex:
            return ToolResult(
                llm_content=f"Error: Invalid regex pattern: {ex}",
                error={"message": f"Invalid regex: {ex}"},
            )

        matches: List[str] = []

        if os.path.isfile(path):
            self._search_file(path, regex, matches, max_results)
        else:
            for root, dirs, files in os.walk(path):
                # Skip hidden and common junk dirs
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".git")]
                for fname in files:
                    if include:
                        import fnmatch
                        if not fnmatch.fnmatch(fname, include):
                            continue
                    fpath = os.path.join(root, fname)
                    self._search_file(fpath, regex, matches, max_results)
                    if len(matches) >= max_results:
                        break
                if len(matches) >= max_results:
                    break

        if not matches:
            return ToolResult(llm_content="No matches found.")

        return ToolResult(
            llm_content=f"Found {len(matches)} matches:\n" + "\n".join(matches)
        )

    @staticmethod
    def _search_file(
        file_path: str, regex: re.Pattern, matches: list, max_results: int
    ) -> None:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    if len(matches) >= max_results:
                        return
                    if regex.search(line):
                        matches.append(f"{file_path}:{line_num}:{line.rstrip()}")
        except (PermissionError, OSError):
            pass
