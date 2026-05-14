"""
Git service for workspace operations.
Provides git status, diff, branch info, repo root detection, and checkpoint/restore (shadow repo).
Ref: gemini-cli/packages/core/src/services/gitService.ts
"""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

from kitten_cli.utils.shell_utils import get_shell_info


async def _run_git(*args: str, cwd: str = ".") -> tuple[int, str, str]:
    """Run a git command asynchronously and return (exit_code, stdout, stderr)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "git", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "PAGER": "cat", "GIT_PAGER": "cat"},
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        return (
            proc.returncode or 0,
            stdout.decode("utf-8", errors="replace").strip(),
            stderr.decode("utf-8", errors="replace").strip(),
        )
    except FileNotFoundError:
        return (1, "", "git: command not found")
    except asyncio.TimeoutError:
        return (1, "", "git: command timed out")


class GitService:
    """
    Provides git operations for workspace management.
    Supports basic git queries (status, diff, branch, log) and
    shadow repository checkpointing for undo/restore.
    """

    SHADOW_AUTHOR_NAME = "Kitten CLI"
    SHADOW_AUTHOR_EMAIL = "kitten-cli@local"

    def __init__(self, project_root: str, history_dir: Optional[str] = None):
        self.project_root = os.path.abspath(project_root)
        self._history_dir = history_dir or os.path.join(
            Path.home(), ".kitten", "history", os.path.basename(self.project_root)
        )

    # ── Static helpers ──

    @staticmethod
    async def verify_git_available() -> bool:
        """Check if git is installed and accessible."""
        code, _, _ = await _run_git("--version")
        return code == 0

    @staticmethod
    async def find_repo_root(start_path: str = ".") -> Optional[str]:
        """Find the root of the git repository containing start_path."""
        code, out, _ = await _run_git("rev-parse", "--show-toplevel", cwd=start_path)
        if code == 0 and out:
            return out
        return None

    @staticmethod
    async def is_git_repo(path: str) -> bool:
        """Check if a directory is inside a git repository."""
        code, _, _ = await _run_git("rev-parse", "--is-inside-work-tree", cwd=path)
        return code == 0

    # ── Basic git queries ──

    async def status(self, short: bool = True) -> str:
        """Get git status output."""
        args = ["status"]
        if short:
            args.append("--short")
        code, out, err = await _run_git(*args, cwd=self.project_root)
        return out if code == 0 else f"Error: {err}"

    async def diff(self, staged: bool = False, name_only: bool = False) -> str:
        """Get git diff output."""
        args = ["diff"]
        if staged:
            args.append("--staged")
        if name_only:
            args.append("--name-only")
        code, out, err = await _run_git(*args, cwd=self.project_root)
        return out if code == 0 else f"Error: {err}"

    async def branch(self) -> str:
        """Get current branch name."""
        code, out, _ = await _run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=self.project_root)
        return out if code == 0 else "unknown"

    async def log(self, n: int = 10, oneline: bool = True) -> str:
        """Get recent commit log."""
        args = ["log", f"-{n}"]
        if oneline:
            args.append("--oneline")
        code, out, err = await _run_git(*args, cwd=self.project_root)
        return out if code == 0 else f"Error: {err}"

    async def get_changed_files(self) -> List[str]:
        """Get list of changed files (both staged and unstaged)."""
        code, out, _ = await _run_git("diff", "--name-only", "HEAD", cwd=self.project_root)
        if code != 0:
            # Maybe no commits yet, try against empty tree
            code, out, _ = await _run_git(
                "diff", "--name-only", "--diff-filter=ACMR",
                cwd=self.project_root
            )
        return [f for f in out.split("\n") if f.strip()] if code == 0 else []

    async def get_repo_info(self) -> Dict[str, Any]:
        """Get comprehensive repo information."""
        branch = await self.branch()
        status = await self.status(short=True)
        root = await self.find_repo_root(self.project_root)
        return {
            "branch": branch,
            "status": status,
            "root": root or self.project_root,
            "is_clean": not bool(status.strip()),
        }

    # ── Shadow Repository (Checkpointing) ──

    def _get_shadow_env(self) -> dict:
        """Get environment variables for shadow repo operations."""
        return {
            **os.environ,
            "GIT_AUTHOR_NAME": self.SHADOW_AUTHOR_NAME,
            "GIT_AUTHOR_EMAIL": self.SHADOW_AUTHOR_EMAIL,
            "GIT_COMMITTER_NAME": self.SHADOW_AUTHOR_NAME,
            "GIT_COMMITTER_EMAIL": self.SHADOW_AUTHOR_EMAIL,
            "GIT_TERMINAL_PROMPT": "0",
            "PAGER": "cat",
        }

    async def initialize_shadow_repo(self) -> None:
        """
        Initialize a shadow git repository for checkpointing.
        The shadow repo tracks the project files independently.
        """
        git_available = await self.verify_git_available()
        if not git_available:
            raise RuntimeError("Git is not installed. Cannot initialize checkpointing.")

        os.makedirs(self._history_dir, exist_ok=True)

        shadow_git = os.path.join(self._history_dir, ".git")
        if not os.path.isdir(shadow_git):
            # Init shadow repo
            proc = await asyncio.create_subprocess_exec(
                "git", "init", "--initial-branch=main",
                cwd=self._history_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._get_shadow_env(),
            )
            await proc.communicate()

            # Initial empty commit
            proc = await asyncio.create_subprocess_exec(
                "git", "commit", "--allow-empty", "-m", "Initial commit",
                cwd=self._history_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self._get_shadow_env(),
            )
            await proc.communicate()

        # Copy .gitignore from project to shadow repo
        project_gitignore = os.path.join(self.project_root, ".gitignore")
        shadow_gitignore = os.path.join(self._history_dir, ".gitignore")
        if os.path.isfile(project_gitignore):
            shutil.copy2(project_gitignore, shadow_gitignore)

    async def create_snapshot(self, message: str = "checkpoint") -> Optional[str]:
        """
        Create a snapshot (checkpoint) of the current project state.
        Returns the commit hash, or None if failed.
        """
        env = {
            **self._get_shadow_env(),
            "GIT_DIR": os.path.join(self._history_dir, ".git"),
            "GIT_WORK_TREE": self.project_root,
        }

        # Stage all changes
        proc = await asyncio.create_subprocess_exec(
            "git", "add", ".",
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        await proc.communicate()

        # Check if there are changes to commit
        proc = await asyncio.create_subprocess_exec(
            "git", "status", "--porcelain",
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, _ = await proc.communicate()
        status_out = stdout.decode("utf-8", errors="replace").strip()

        if not status_out:
            # No changes, return current HEAD
            proc = await asyncio.create_subprocess_exec(
                "git", "rev-parse", "HEAD",
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            stdout, _ = await proc.communicate()
            return stdout.decode("utf-8", errors="replace").strip() or None

        # Commit changes
        proc = await asyncio.create_subprocess_exec(
            "git", "commit", "--no-verify", "-m", message,
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            # Get the commit hash
            proc2 = await asyncio.create_subprocess_exec(
                "git", "rev-parse", "HEAD",
                cwd=self.project_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            stdout2, _ = await proc2.communicate()
            return stdout2.decode("utf-8", errors="replace").strip() or None
        return None

    async def restore_snapshot(self, commit_hash: str) -> bool:
        """
        Restore the project to a previous snapshot.
        Returns True on success.
        """
        env = {
            **self._get_shadow_env(),
            "GIT_DIR": os.path.join(self._history_dir, ".git"),
            "GIT_WORK_TREE": self.project_root,
        }

        # Restore files
        proc = await asyncio.create_subprocess_exec(
            "git", "restore", "--source", commit_hash, ".",
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        await proc.communicate()

        # Clean untracked files
        proc = await asyncio.create_subprocess_exec(
            "git", "clean", "-fd",
            cwd=self.project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        await proc.communicate()

        return proc.returncode == 0
