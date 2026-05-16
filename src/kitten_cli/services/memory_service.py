"""
Memory service — manages KITTEN.md files for persistent agent memory.
Ref: gemini-cli/packages/core/src/services/memoryService.ts (GEMINI.md)

Memory files provide persistent, cross-session context:
- Global: ~/.kitten/KITTEN.md (user preferences across all projects)
- Project: <workspace>/KITTEN.md (project-specific instructions)
- Nested: Any KITTEN.md found walking up from cwd to project root
"""

import os
from pathlib import Path
from typing import List, Optional


MEMORY_FILE_NAME = "KITTEN.md"
GLOBAL_MEMORY_DIR = str(Path.home() / ".kitten")


class MemoryService:
    """
    Manages KITTEN.md memory files for persistent agent context.
    Supports hierarchical discovery (project + global) and read/write operations.
    """

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = os.path.abspath(project_root) if project_root else os.getcwd()

    # ── Discovery ──

    def get_global_memory_path(self) -> str:
        """Get path to global KITTEN.md."""
        return os.path.join(GLOBAL_MEMORY_DIR, MEMORY_FILE_NAME)

    def get_project_memory_path(self) -> str:
        """Get path to project-level KITTEN.md."""
        return os.path.join(self.project_root, MEMORY_FILE_NAME)

    def discover_memory_files(self) -> List[str]:
        """
        Discover all KITTEN.md files in order of precedence (most specific last):
        1. Global (~/.kitten/KITTEN.md)
        2. Walking up from project root to filesystem root
        3. Project root (KITTEN.md)
        
        Returns list of existing file paths.
        """
        paths: List[str] = []

        # 1. Global
        global_path = self.get_global_memory_path()
        if os.path.isfile(global_path):
            paths.append(global_path)

        # 2. Walk up from project root (collecting any KITTEN.md in parent dirs)
        #    Stop at filesystem root or home directory
        current = self.project_root
        home = str(Path.home())
        ancestors: List[str] = []

        while True:
            candidate = os.path.join(current, MEMORY_FILE_NAME)
            if os.path.isfile(candidate) and candidate != global_path:
                ancestors.append(candidate)

            parent = os.path.dirname(current)
            if parent == current or current == home:
                break
            current = parent

        # Add ancestors in reverse (broadest first, project-level last)
        paths.extend(reversed(ancestors))

        return paths

    # ── Read ──

    def load_all_memory(self) -> str:
        """
        Load and concatenate all discovered memory files.
        Returns combined content with section headers.
        """
        files = self.discover_memory_files()
        if not files:
            return ""

        sections: List[str] = []
        for fpath in files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    # Label each section with its source
                    label = "Global" if ".kitten" in fpath else os.path.relpath(fpath, self.project_root)
                    sections.append(f"<!-- Memory: {label} -->\n{content}")
            except (OSError, UnicodeDecodeError):
                continue

        return "\n\n".join(sections)

    def load_memory(self, path: Optional[str] = None) -> str:
        """Load a single memory file. Defaults to project-level."""
        target = path or self.get_project_memory_path()
        try:
            with open(target, "r", encoding="utf-8") as f:
                return f.read().strip()
        except (FileNotFoundError, UnicodeDecodeError):
            return ""

    # ── Write ──

    def save_memory(self, content: str, path: Optional[str] = None) -> str:
        """
        Save content to a memory file.
        Defaults to project-level KITTEN.md.
        Returns the path written to.
        """
        target = path or self.get_project_memory_path()
        os.makedirs(os.path.dirname(target), exist_ok=True)

        with open(target, "w", encoding="utf-8") as f:
            f.write(content)

        return target

    def append_memory(self, content: str, path: Optional[str] = None) -> str:
        """
        Append content to a memory file.
        Defaults to project-level KITTEN.md.
        """
        target = path or self.get_project_memory_path()
        os.makedirs(os.path.dirname(target), exist_ok=True)

        existing = self.load_memory(target)
        new_content = f"{existing}\n\n{content}" if existing else content

        with open(target, "w", encoding="utf-8") as f:
            f.write(new_content)

        return target

    def save_global_memory(self, content: str) -> str:
        """Save to global memory."""
        return self.save_memory(content, self.get_global_memory_path())

    # ── Info ──

    def get_memory_info(self) -> dict:
        """Get info about all discovered memory files."""
        files = self.discover_memory_files()
        info = {
            "files": [],
            "total_files": len(files),
            "global_exists": os.path.isfile(self.get_global_memory_path()),
            "project_exists": os.path.isfile(self.get_project_memory_path()),
        }

        for fpath in files:
            try:
                stat = os.stat(fpath)
                info["files"].append({
                    "path": fpath,
                    "size": stat.st_size,
                    "is_global": ".kitten" in fpath,
                })
            except OSError:
                continue

        return info
