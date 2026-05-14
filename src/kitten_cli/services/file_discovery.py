"""
File discovery service for workspace scanning.
Scans directory trees while respecting .gitignore, .kittenignore, and custom ignore patterns.
Ref: gemini-cli/packages/core/src/services/fileDiscoveryService.ts
"""

import os
import stat
from pathlib import Path
from typing import List, Optional, Set, Dict, Any

from kitten_cli.utils.ignore_patterns import IgnorePatterns

# Maximum number of files to discover to prevent runaway scanning
MAX_DISCOVERY_FILES = 50_000

# Maximum directory depth to scan
MAX_DEPTH = 20

# File extensions considered binary (skip content reading)
BINARY_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".flv", ".wav", ".ogg",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".dat",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pyc", ".pyo", ".class", ".o", ".obj",
    ".sqlite", ".db", ".sqlite3",
    ".lock",
})


class FileDiscoveryService:
    """
    Scans workspace directory trees for relevant files.
    Respects .gitignore, .kittenignore, and custom ignore patterns.
    Provides filtering APIs for file lists.
    """

    def __init__(
        self,
        project_root: str,
        respect_gitignore: bool = True,
        respect_kittenignore: bool = True,
        custom_ignore_patterns: Optional[List[str]] = None,
    ):
        self.project_root = os.path.abspath(project_root)
        self.respect_gitignore = respect_gitignore
        self.respect_kittenignore = respect_kittenignore

        # Build combined ignore patterns
        extra_patterns = list(custom_ignore_patterns or [])
        self._ignore = IgnorePatterns.from_directory(self.project_root)
        if custom_ignore_patterns:
            for p in custom_ignore_patterns:
                self._ignore._patterns.append(p)

    def discover_files(
        self,
        max_files: int = MAX_DISCOVERY_FILES,
        max_depth: int = MAX_DEPTH,
        include_hidden: bool = False,
    ) -> List[str]:
        """
        Walk the project directory and return a list of relative file paths.
        Respects ignore patterns and depth limits.
        """
        found: List[str] = []

        def _walk(current_dir: str, depth: int) -> None:
            if depth > max_depth or len(found) >= max_files:
                return

            try:
                entries = sorted(os.scandir(current_dir), key=lambda e: e.name)
            except (PermissionError, OSError):
                return

            for entry in entries:
                if len(found) >= max_files:
                    return

                name = entry.name

                # Skip hidden files/dirs unless requested
                if not include_hidden and name.startswith("."):
                    continue

                rel_path = os.path.relpath(entry.path, self.project_root)
                # Normalize to forward slashes for consistency
                rel_path = rel_path.replace("\\", "/")

                if entry.is_dir(follow_symlinks=False):
                    if self._ignore.is_ignored(rel_path, is_dir=True):
                        continue
                    _walk(entry.path, depth + 1)
                elif entry.is_file(follow_symlinks=False):
                    if self._ignore.is_ignored(rel_path, is_dir=False):
                        continue
                    found.append(rel_path)

        _walk(self.project_root, 0)
        return found

    def discover_with_metadata(
        self,
        max_files: int = MAX_DISCOVERY_FILES,
        max_depth: int = MAX_DEPTH,
    ) -> List[Dict[str, Any]]:
        """
        Discover files and return metadata (path, size, extension, is_binary).
        """
        files = self.discover_files(max_files=max_files, max_depth=max_depth)
        result = []
        for rel_path in files:
            abs_path = os.path.join(self.project_root, rel_path)
            try:
                st = os.stat(abs_path)
                ext = os.path.splitext(rel_path)[1].lower()
                result.append({
                    "path": rel_path,
                    "size": st.st_size,
                    "extension": ext,
                    "is_binary": ext in BINARY_EXTENSIONS,
                })
            except OSError:
                continue
        return result

    def filter_files(self, file_paths: List[str]) -> List[str]:
        """Filter a list of file paths based on ignore rules."""
        return [
            p for p in file_paths
            if not self._ignore.is_ignored(p, is_dir=False)
        ]

    def filter_files_with_report(self, file_paths: List[str]) -> Dict[str, Any]:
        """Filter files and return a report with counts."""
        filtered = self.filter_files(file_paths)
        return {
            "filtered_paths": filtered,
            "ignored_count": len(file_paths) - len(filtered),
            "total_count": len(file_paths),
        }

    def should_ignore_file(self, file_path: str) -> bool:
        """Check if a specific file should be ignored."""
        return self._ignore.is_ignored(file_path, is_dir=False)

    def should_ignore_directory(self, dir_path: str) -> bool:
        """Check if a specific directory should be ignored."""
        return self._ignore.is_ignored(dir_path, is_dir=True)

    def get_ignore_file_paths(self) -> List[str]:
        """Return paths of ignore files being used."""
        paths = []
        for name in (".gitignore", ".kittenignore"):
            p = os.path.join(self.project_root, name)
            if os.path.isfile(p):
                paths.append(p)
        return paths

    @staticmethod
    def is_binary_file(file_path: str) -> bool:
        """Check if a file is binary by extension."""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in BINARY_EXTENSIONS

    def get_folder_structure(
        self,
        max_depth: int = 3,
        max_entries: int = 200,
    ) -> str:
        """
        Build a tree-like string representation of the project folder structure.
        Useful for providing workspace context to the LLM.
        """
        lines: List[str] = []
        count = 0

        def _tree(directory: str, prefix: str, depth: int) -> None:
            nonlocal count
            if depth > max_depth or count >= max_entries:
                return

            try:
                entries = sorted(os.scandir(directory), key=lambda e: (not e.is_dir(), e.name))
            except (PermissionError, OSError):
                return

            # Filter out ignored entries
            visible = []
            for entry in entries:
                if entry.name.startswith("."):
                    continue
                rel = os.path.relpath(entry.path, self.project_root).replace("\\", "/")
                is_dir = entry.is_dir(follow_symlinks=False)
                if not self._ignore.is_ignored(rel, is_dir=is_dir):
                    visible.append(entry)

            for i, entry in enumerate(visible):
                if count >= max_entries:
                    lines.append(f"{prefix}... (truncated)")
                    return

                is_last = (i == len(visible) - 1)
                connector = "+-- " if is_last else "|-- "
                extension = "    " if is_last else "|   "

                if entry.is_dir(follow_symlinks=False):
                    lines.append(f"{prefix}{connector}{entry.name}/")
                    count += 1
                    _tree(entry.path, prefix + extension, depth + 1)
                else:
                    lines.append(f"{prefix}{connector}{entry.name}")
                    count += 1

        root_name = os.path.basename(self.project_root)
        lines.append(f"{root_name}/")
        count += 1
        _tree(self.project_root, "", 0)

        return "\n".join(lines)
