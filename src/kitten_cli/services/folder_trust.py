"""
Folder trust service — manages workspace trust for security.
Ref: gemini-cli/packages/core/src/services/FolderTrustDiscoveryService.ts

When the user opens a workspace for the first time, kitten-cli should
ask whether to trust the folder. Untrusted folders may have restricted
tool access (e.g., no shell execution, no file writes).
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set


TRUST_FILE = "trusted_folders.json"


class FolderTrustService:
    """
    Manages a list of trusted workspace folders.
    Trust is persisted to ~/.kitten/trusted_folders.json.
    """

    def __init__(self, config_dir: Optional[str] = None):
        self._config_dir = config_dir or str(Path.home() / ".kitten")
        self._trust_file = os.path.join(self._config_dir, TRUST_FILE)
        self._trusted: Set[str] = set()
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy-load the trust file."""
        if self._loaded:
            return
        self._loaded = True

        if not os.path.isfile(self._trust_file):
            return

        try:
            with open(self._trust_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self._trusted = {os.path.normpath(p) for p in data}
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self) -> None:
        """Persist trust data to disk."""
        os.makedirs(self._config_dir, exist_ok=True)
        with open(self._trust_file, "w", encoding="utf-8") as f:
            json.dump(sorted(self._trusted), f, indent=2)

    def is_trusted(self, folder: str) -> bool:
        """Check if a folder is trusted."""
        self._ensure_loaded()
        normalized = os.path.normpath(os.path.abspath(folder))

        # Check exact match or if it's a subdirectory of a trusted folder
        for trusted in self._trusted:
            if normalized == trusted or normalized.startswith(trusted + os.sep):
                return True
        return False

    def trust_folder(self, folder: str) -> None:
        """Mark a folder as trusted."""
        self._ensure_loaded()
        normalized = os.path.normpath(os.path.abspath(folder))
        self._trusted.add(normalized)
        self._save()

    def untrust_folder(self, folder: str) -> None:
        """Remove trust from a folder."""
        self._ensure_loaded()
        normalized = os.path.normpath(os.path.abspath(folder))
        self._trusted.discard(normalized)
        self._save()

    def list_trusted(self) -> List[str]:
        """List all trusted folders."""
        self._ensure_loaded()
        return sorted(self._trusted)

    def needs_trust_prompt(self, folder: str) -> bool:
        """
        Check if the user should be prompted to trust this folder.
        Returns True if the folder is not trusted and is not a subdirectory of a trusted folder.
        """
        return not self.is_trusted(folder)
