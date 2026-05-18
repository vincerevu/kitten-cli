"""
Scoped config — per-project config overrides with layered resolution.
Ref: gemini-cli/packages/core/src/config/scoped-config.ts

Resolution order (later wins):
  1. Built-in defaults (constants.py)
  2. Global settings (~/.kitten/settings.json)
  3. Project config (.kitten.toml)
  4. CLI arguments
  5. Environment variables
"""

import os
from typing import Any, Dict, Optional

from kitten_cli.config.settings import AppConfig, LLMConfig, ApprovalMode
from kitten_cli.config.loader import load_json, load_toml
from kitten_cli.config.schema import SettingsSchema, ProjectConfig
from kitten_cli.config.constants import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MAX_TURNS,
    DEFAULT_MAX_TIME_MINUTES,
)


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base, returning a new dict."""
    merged = dict(base)
    for key, val in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(val, dict):
            merged[key] = _deep_merge(merged[key], val)
        else:
            merged[key] = val
    return merged


def load_global_settings(home_dir: Optional[str] = None) -> Dict[str, Any]:
    """Load global settings from ~/.kitten/settings.json."""
    home = home_dir or os.path.expanduser("~/.kitten")
    path = os.path.join(home, "settings.json")
    return load_json(path) or {}


def load_project_config(project_root: Optional[str] = None) -> Dict[str, Any]:
    """Load project config from .kitten.toml in the project root."""
    root = project_root or os.getcwd()
    path = os.path.join(root, ".kitten.toml")
    return load_toml(path) or {}


def load_env_overrides() -> Dict[str, Any]:
    """Load config overrides from environment variables."""
    overrides: Dict[str, Any] = {}

    env_map = {
        "KITTEN_MODEL": "model",
        "KITTEN_API_KEY": "api_key",
        "KITTEN_BASE_URL": "base_url",
        "KITTEN_TEMPERATURE": "temperature",
        "KITTEN_MAX_TURNS": "max_turns",
        "KITTEN_APPROVAL_MODE": "approval_mode",
    }

    for env_var, config_key in env_map.items():
        val = os.environ.get(env_var)
        if val is not None:
            # Type coercion
            if config_key == "temperature":
                try:
                    overrides[config_key] = float(val)
                except ValueError:
                    pass
            elif config_key == "max_turns":
                try:
                    overrides[config_key] = int(val)
                except ValueError:
                    pass
            else:
                overrides[config_key] = val

    return overrides


def resolve_config(
    project_root: Optional[str] = None,
    cli_args: Optional[Dict[str, Any]] = None,
    home_dir: Optional[str] = None,
) -> SettingsSchema:
    """
    Resolve the final configuration by merging all layers.
    
    Resolution order (later wins):
    1. Built-in defaults
    2. Global settings.json
    3. Project .kitten.toml
    4. CLI arguments
    5. Environment variables
    """
    # Layer 1: Defaults (handled by SettingsSchema defaults)
    config: Dict[str, Any] = {}

    # Layer 2: Global settings
    global_settings = load_global_settings(home_dir)
    config = _deep_merge(config, global_settings)

    # Layer 3: Project config
    project_config = load_project_config(project_root)
    config = _deep_merge(config, project_config)

    # Layer 4: CLI arguments
    if cli_args:
        # Filter out None values from CLI args
        cli_overrides = {k: v for k, v in cli_args.items() if v is not None}
        config = _deep_merge(config, cli_overrides)

    # Layer 5: Environment variables
    env_overrides = load_env_overrides()
    config = _deep_merge(config, env_overrides)

    # Validate and return
    return SettingsSchema(**config)


def settings_to_app_config(settings: SettingsSchema) -> AppConfig:
    """Convert a SettingsSchema to an AppConfig for backward compatibility."""
    return AppConfig(
        llm=LLMConfig(
            model=settings.model,
            api_key=settings.api_key,
            base_url=settings.base_url,
            temperature=settings.temperature,
            max_output_tokens=settings.max_output_tokens,
        ),
        max_iterations=settings.max_turns,
        theme=settings.theme,
    )
