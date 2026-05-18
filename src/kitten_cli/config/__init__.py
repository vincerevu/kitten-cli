"""Configuration system — loader, manager, schema, settings, storage, constants, scoped config."""

from kitten_cli.config.settings import ApprovalMode, LLMConfig, AppConfig
from kitten_cli.config.schema import PolicyRule, ProjectConfig, McpServerConfig, SettingsSchema
from kitten_cli.config.manager import ConfigManager
from kitten_cli.config.storage import Storage
from kitten_cli.config.scoped_config import resolve_config, settings_to_app_config
from kitten_cli.config.constants import (
    DEFAULT_MODEL,
    DEFAULT_MAX_TURNS,
    DEFAULT_MAX_TIME_MINUTES,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_CONTEXT_WINDOW,
    DEFAULT_COMPACTION_THRESHOLD,
    DEFAULT_PRUNING_THRESHOLD,
    DEFAULT_TOOL_TIMEOUT,
)

__all__ = [
    "ApprovalMode",
    "LLMConfig",
    "AppConfig",
    "PolicyRule",
    "ProjectConfig",
    "McpServerConfig",
    "SettingsSchema",
    "ConfigManager",
    "Storage",
    "resolve_config",
    "settings_to_app_config",
    "DEFAULT_MODEL",
    "DEFAULT_MAX_TURNS",
    "DEFAULT_MAX_TIME_MINUTES",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_OUTPUT_TOKENS",
    "DEFAULT_CONTEXT_WINDOW",
    "DEFAULT_COMPACTION_THRESHOLD",
    "DEFAULT_PRUNING_THRESHOLD",
    "DEFAULT_TOOL_TIMEOUT",
]
