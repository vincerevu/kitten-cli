"""
ShellTool — Execute shell commands.
Ref: gemini-cli/packages/core/src/tools/shell.ts
"""
import asyncio
import os
import platform
from typing import Any, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class ShellTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="run_command",
            display_name="Run Command",
            description="Execute a shell command and return stdout/stderr. Commands run in the workspace directory.",
            kind=ToolKind.EXEC,
            parameter_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute.",
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory for the command. Defaults to workspace root.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds. Default 120.",
                    },
                },
                "required": ["command"],
            },
        )
        self._default_cwd: str = os.getcwd()

    def set_default_cwd(self, cwd: str) -> None:
        self._default_cwd = cwd

    async def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 120,
        **kwargs: Any,
    ) -> ToolResult:
        work_dir = os.path.abspath(cwd) if cwd else self._default_cwd

        if not os.path.isdir(work_dir):
            return ToolResult(
                llm_content=f"Error: Working directory not found: {work_dir}",
                error={"message": f"Directory not found: {work_dir}"},
            )

        is_windows = platform.system() == "Windows"
        if is_windows:
            shell_cmd = ["powershell", "-NoProfile", "-Command", command]
        else:
            shell_cmd = ["/bin/bash", "-c", command]

        try:
            process = await asyncio.create_subprocess_exec(
                *shell_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir,
                env={**os.environ, "PAGER": "cat"},
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            try:
                process.kill()
            except Exception:
                pass
            return ToolResult(
                llm_content=f"Error: Command timed out after {timeout}s: {command}",
                error={"message": f"Timeout after {timeout}s", "type": "timeout"},
            )
        except Exception as ex:
            return ToolResult(
                llm_content=f"Error executing command: {ex}",
                error={"message": str(ex)},
            )

        stdout_str = stdout.decode("utf-8", errors="replace").strip() if stdout else ""
        stderr_str = stderr.decode("utf-8", errors="replace").strip() if stderr else ""
        exit_code = process.returncode or 0

        # Truncate very long outputs
        max_output = 40000
        if len(stdout_str) > max_output:
            stdout_str = stdout_str[:max_output] + f"\n... [truncated, {len(stdout_str)} total chars]"
        if len(stderr_str) > max_output:
            stderr_str = stderr_str[:max_output] + f"\n... [truncated, {len(stderr_str)} total chars]"

        parts = []
        if stdout_str:
            parts.append(f"stdout:\n{stdout_str}")
        if stderr_str:
            parts.append(f"stderr:\n{stderr_str}")
        parts.append(f"Exit code: {exit_code}")

        output = "\n\n".join(parts)

        if exit_code != 0:
            return ToolResult(
                llm_content=output,
                error={"message": f"Command exited with code {exit_code}"},
            )

        return ToolResult(llm_content=output)
