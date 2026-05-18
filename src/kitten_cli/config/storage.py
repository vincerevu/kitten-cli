"""
Storage service — manages data directories and paths.
Ref: gemini-cli/packages/core/src/config/storage.ts

Centralized path management for all kitten-cli persistent data:
  ~/.kitten/
    settings.json       — global user settings
    sessions/           — JSONL conversation recordings
    history/<project>/  — shadow git repos per project
    tmp/                — temporary files (background process logs)
    trusted_folders.json
    KITTEN.md           — global memory
"""

import os
from pathlib import Path
from typing import Optional


# Base directory
KITTEN_HOME = str(Path.home() / ".kitten")


class Storage:
    """
    Manages all persistent data paths for kitten-cli.
    Creates directories on demand.
    """

    def __init__(
        self,
        home_dir: Optional[str] = None,
        project_root: Optional[str] = None,
    ):
        self.home_dir = home_dir or KITTEN_HOME
        self.project_root = os.path.abspath(project_root) if project_root else os.getcwd()
        self._project_name = os.path.basename(self.project_root)

    def initialize(self) -> None:
        """Create all necessary directories."""
        for d in [
            self.home_dir,
            self.get_sessions_dir(),
            self.get_history_dir(),
            self.get_temp_dir(),
        ]:
            os.makedirs(d, exist_ok=True)

    # ── Path getters ──

    def get_settings_path(self) -> str:
        """Global settings.json path."""
        return os.path.join(self.home_dir, "settings.json")

    def get_project_config_path(self) -> str:
        """Per-project .kitten.toml path."""
        return os.path.join(self.project_root, ".kitten.toml")

    def get_sessions_dir(self) -> str:
        """Directory for conversation JSONL files."""
        return os.path.join(self.home_dir, "sessions")

    def get_history_dir(self) -> str:
        """Shadow git repo directory for this project."""
        return os.path.join(self.home_dir, "history", self._project_name)

    def get_temp_dir(self) -> str:
        """Temporary files directory."""
        return os.path.join(self.home_dir, "tmp")

    def get_background_logs_dir(self) -> str:
        """Background process log files."""
        d = os.path.join(self.get_temp_dir(), "background-processes")
        os.makedirs(d, exist_ok=True)
        return d

    def get_tool_outputs_dir(self) -> str:
        """Pruned tool output offload directory."""
        d = os.path.join(self.get_temp_dir(), "tool-outputs")
        os.makedirs(d, exist_ok=True)
        return d

    def get_global_memory_path(self) -> str:
        """Global KITTEN.md path."""
        return os.path.join(self.home_dir, "KITTEN.md")

    def get_project_memory_path(self) -> str:
        """Project-level KITTEN.md path."""
        return os.path.join(self.project_root, "KITTEN.md")

    def get_trust_file_path(self) -> str:
        """trusted_folders.json path."""
        return os.path.join(self.home_dir, "trusted_folders.json")

    @staticmethod
    def get_global_temp_dir() -> str:
        """Class-level temp dir accessor (no project context needed)."""
        d = os.path.join(KITTEN_HOME, "tmp")
        os.makedirs(d, exist_ok=True)
        return d
