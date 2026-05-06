"""
Ignore patterns — .gitignore / .kittenignore parsing.
Ref: gemini-cli/packages/core/src/utils/ignorePatterns.ts
Ref: gemini-cli/packages/core/src/utils/gitIgnoreParser.ts
"""
import os
import fnmatch
from typing import List, Optional, Set


# Default patterns always ignored
DEFAULT_IGNORE_PATTERNS = [
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".env",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "*.egg-info",
    ".DS_Store",
    "Thumbs.db",
]


class IgnorePatterns:
    """Parse and match ignore patterns from .gitignore / .kittenignore files."""

    def __init__(self, patterns: Optional[List[str]] = None):
        self._patterns: List[str] = list(DEFAULT_IGNORE_PATTERNS)
        if patterns:
            self._patterns.extend(patterns)

    @classmethod
    def from_file(cls, path: str) -> "IgnorePatterns":
        """Load patterns from a .gitignore-style file."""
        patterns = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except FileNotFoundError:
            pass
        return cls(patterns)

    @classmethod
    def from_directory(cls, directory: str) -> "IgnorePatterns":
        """Load patterns from .gitignore and .kittenignore in a directory."""
        patterns = []
        for filename in (".gitignore", ".kittenignore"):
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                patterns.append(line)
                except Exception:
                    pass
        return cls(patterns)

    def is_ignored(self, path: str, is_dir: bool = False) -> bool:
        """Check if a path matches any ignore pattern."""
        basename = os.path.basename(path)
        for pattern in self._patterns:
            # Handle negation
            if pattern.startswith("!"):
                continue  # Skip negation for now (simplified)

            # Match against basename
            if fnmatch.fnmatch(basename, pattern):
                return True

            # Match against full relative path
            if fnmatch.fnmatch(path, pattern):
                return True

            # Handle directory patterns (ending with /)
            if pattern.endswith("/") and is_dir:
                if fnmatch.fnmatch(basename, pattern.rstrip("/")):
                    return True

        return False

    def filter_paths(self, paths: List[str]) -> List[str]:
        """Return only non-ignored paths."""
        return [p for p in paths if not self.is_ignored(p, os.path.isdir(p))]
