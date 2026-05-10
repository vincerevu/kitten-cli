
import os
import json
from typing import Any, Dict, Optional

import tomlkit


def load_toml(path: str) -> Optional[Dict[str, Any]]:
    """Load and parse a TOML file, return None on failure."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return dict(tomlkit.load(f))
    except Exception:
        return None


def load_json(path: str) -> Optional[Dict[str, Any]]:
    """Load and parse a JSON file (settings.json), return None on failure."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, Exception):
        return None


def load_config_file(path: str) -> Optional[Dict[str, Any]]:
    """Auto-detect file type and load config."""
    if path.endswith(".toml"):
        return load_toml(path)
    elif path.endswith(".json"):
        return load_json(path)
    # Try TOML first, then JSON
    result = load_toml(path)
    if result is not None:
        return result
    return load_json(path)


def find_config_files(directory: str) -> list:
    """Find all config files in a directory (settings.json, config.toml, .kitten.toml)."""
    candidates = [
        os.path.join(directory, "config.toml"),
        os.path.join(directory, ".kitten.toml"),
        os.path.join(directory, "settings.json"),
    ]
    return [p for p in candidates if os.path.exists(p)]
