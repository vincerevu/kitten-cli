"""
Shell execution service for advanced process management.
Handles PTY-like spawning, timeouts, streaming output, background process tracking.
Ref: gemini-cli/packages/core/src/services/shellExecutionService.ts

Note: gemini-cli's shellExecutionService.ts is 1600+ lines with node-pty, xterm headless terminal,
sandbox integration, and background process lifecycle management. This Python version provides
a practical equivalent using asyncio subprocess with streaming, background tracking, and log files.
"""

import asyncio
import os
import platform
import signal
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple

from kitten_cli.utils.shell_utils import get_shell_info, sanitize_for_display


# ── Constants ──

MAX_OUTPUT_BUFFER = 16 * 1024 * 1024  # 16MB
DEFAULT_TIMEOUT = 120  # seconds
KITTEN_CLI_ENV_VAR = "KITTEN_CLI"
KITTEN_CLI_ENV_VAR_VALUE = "1"


# ── Types ──

class ProcessStatus(str, Enum):
    RUNNING = "running"
    EXITED = "exited"
    TIMEOUT = "timeout"
    KILLED = "killed"


@dataclass
class ShellResult:
    """Result of a shell command execution."""
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    timed_out: bool = False
    killed: bool = False
    pid: Optional[int] = None
    duration_ms: int = 0


@dataclass
class BackgroundProcess:
    """Tracks a background process."""
    pid: int
    command: str
    status: ProcessStatus = ProcessStatus.RUNNING
    exit_code: Optional[int] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    log_path: Optional[str] = None
    session_id: str = "default"


class ShellExecutionService:
    """
    Centralized service for executing shell commands with:
    - Streaming output events
    - Background process tracking
    - Log file management
    - Timeout handling
    - Cross-platform shell detection
    """

    # Class-level tracking of background processes across all instances
    _background_processes: Dict[int, BackgroundProcess] = {}

    def __init__(
        self,
        default_cwd: Optional[str] = None,
        default_timeout: int = DEFAULT_TIMEOUT,
        log_dir: Optional[str] = None,
    ):
        self.default_cwd = default_cwd or os.getcwd()
        self.default_timeout = default_timeout
        self.log_dir = log_dir or str(
            Path.home() / ".kitten" / "tmp" / "background-processes"
        )
        os.makedirs(self.log_dir, exist_ok=True)

    def _get_shell_cmd(self, command: str) -> List[str]:
        """Get platform-appropriate shell command."""
        info = get_shell_info()
        return info["shell_cmd"] + [command]

    def _get_env(self, extra_env: Optional[Dict[str, str]] = None) -> dict:
        """Build execution environment."""
        env = {
            **os.environ,
            KITTEN_CLI_ENV_VAR: KITTEN_CLI_ENV_VAR_VALUE,
            "PAGER": "cat",
            "GIT_PAGER": "cat",
            "GIT_TERMINAL_PROMPT": "0",
        }
        if extra_env:
            env.update(extra_env)
        return env

    async def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> ShellResult:
        """
        Execute a shell command and return the complete result.
        Blocks until the command finishes or times out.
        """
        work_dir = os.path.abspath(cwd) if cwd else self.default_cwd
        timeout_sec = timeout if timeout is not None else self.default_timeout
        shell_cmd = self._get_shell_cmd(command)
        exec_env = self._get_env(env)

        start_time = time.monotonic()

        try:
            proc = await asyncio.create_subprocess_exec(
                *shell_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir,
                env=exec_env,
            )
        except FileNotFoundError as e:
            return ShellResult(
                stderr=f"Command not found: {e}",
                exit_code=127,
            )
        except Exception as e:
            return ShellResult(
                stderr=f"Failed to start process: {e}",
                exit_code=1,
            )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout_sec
            )
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            elapsed = int((time.monotonic() - start_time) * 1000)
            return ShellResult(
                stderr=f"Command timed out after {timeout_sec}s",
                exit_code=None,
                timed_out=True,
                pid=proc.pid,
                duration_ms=elapsed,
            )

        elapsed = int((time.monotonic() - start_time) * 1000)
        stdout = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
        stderr = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""

        # Truncate excessively long outputs
        if len(stdout) > MAX_OUTPUT_BUFFER:
            stdout = stdout[:MAX_OUTPUT_BUFFER] + f"\n[Truncated. Total: {len(stdout)} chars]"
        if len(stderr) > MAX_OUTPUT_BUFFER:
            stderr = stderr[:MAX_OUTPUT_BUFFER] + f"\n[Truncated. Total: {len(stderr)} chars]"

        return ShellResult(
            stdout=stdout.strip(),
            stderr=stderr.strip(),
            exit_code=proc.returncode,
            pid=proc.pid,
            duration_ms=elapsed,
        )

    async def execute_streaming(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a shell command and yield streaming output events.
        Events: {"type": "stdout"|"stderr"|"exit", "data": str, ...}
        """
        work_dir = os.path.abspath(cwd) if cwd else self.default_cwd
        timeout_sec = timeout if timeout is not None else self.default_timeout
        shell_cmd = self._get_shell_cmd(command)
        exec_env = self._get_env(env)

        proc = await asyncio.create_subprocess_exec(
            *shell_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
            env=exec_env,
        )

        start_time = time.monotonic()

        async def read_stream(stream, stream_name: str):
            while True:
                line = await stream.readline()
                if not line:
                    break
                yield {"type": stream_name, "data": line.decode("utf-8", errors="replace")}

        # Read stdout and stderr concurrently
        stdout_buffer = []
        stderr_buffer = []

        async def _read_stdout():
            async for event in read_stream(proc.stdout, "stdout"):
                stdout_buffer.append(event["data"])
                yield event

        async def _read_stderr():
            async for event in read_stream(proc.stderr, "stderr"):
                stderr_buffer.append(event["data"])
                yield event

        # Yield stdout events
        async for event in _read_stdout():
            yield event

        # Wait for process to complete
        try:
            await asyncio.wait_for(proc.wait(), timeout=timeout_sec)
        except asyncio.TimeoutError:
            proc.kill()
            yield {"type": "exit", "exit_code": None, "timed_out": True}
            return

        elapsed = int((time.monotonic() - start_time) * 1000)
        yield {
            "type": "exit",
            "exit_code": proc.returncode,
            "duration_ms": elapsed,
        }

    async def execute_background(
        self,
        command: str,
        cwd: Optional[str] = None,
        session_id: str = "default",
        env: Optional[Dict[str, str]] = None,
    ) -> BackgroundProcess:
        """
        Start a command in the background, tracking it and logging output.
        Returns a BackgroundProcess record immediately.
        """
        work_dir = os.path.abspath(cwd) if cwd else self.default_cwd
        shell_cmd = self._get_shell_cmd(command)
        exec_env = self._get_env(env)

        proc = await asyncio.create_subprocess_exec(
            *shell_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
            env=exec_env,
        )

        pid = proc.pid or 0
        log_path = os.path.join(self.log_dir, f"background-{pid}.log")

        bg = BackgroundProcess(
            pid=pid,
            command=sanitize_for_display(command),
            log_path=log_path,
            session_id=session_id,
        )
        self._background_processes[pid] = bg

        # Start background log collection task
        asyncio.create_task(self._collect_background_output(proc, bg))

        return bg

    async def _collect_background_output(
        self, proc: asyncio.subprocess.Process, bg: BackgroundProcess
    ) -> None:
        """Collect output from a background process and write to log file."""
        try:
            with open(bg.log_path, "w", encoding="utf-8") as log_file:
                async def _read(stream):
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        decoded = line.decode("utf-8", errors="replace")
                        log_file.write(decoded)
                        log_file.flush()

                await asyncio.gather(
                    _read(proc.stdout),
                    _read(proc.stderr),
                )

            await proc.wait()

            bg.status = ProcessStatus.EXITED
            bg.exit_code = proc.returncode
            bg.end_time = time.time()

        except Exception:
            bg.status = ProcessStatus.KILLED
            bg.end_time = time.time()

    def get_background_processes(self, session_id: Optional[str] = None) -> List[BackgroundProcess]:
        """Get all tracked background processes, optionally filtered by session."""
        procs = list(self._background_processes.values())
        if session_id:
            procs = [p for p in procs if p.session_id == session_id]
        return procs

    def get_background_process(self, pid: int) -> Optional[BackgroundProcess]:
        """Get a specific background process by PID."""
        return self._background_processes.get(pid)

    @classmethod
    def kill_background_process(cls, pid: int) -> bool:
        """Kill a background process by PID."""
        bg = cls._background_processes.get(pid)
        if not bg or bg.status != ProcessStatus.RUNNING:
            return False

        try:
            if platform.system() == "Windows":
                os.system(f"taskkill /F /T /PID {pid}")
            else:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            bg.status = ProcessStatus.KILLED
            bg.end_time = time.time()
            return True
        except (ProcessLookupError, PermissionError, OSError):
            bg.status = ProcessStatus.KILLED
            bg.end_time = time.time()
            return False

    @classmethod
    def cleanup_all(cls) -> None:
        """Kill all tracked background processes."""
        for pid in list(cls._background_processes.keys()):
            cls.kill_background_process(pid)
