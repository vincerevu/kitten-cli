"""Slash command system — /help, /clear, /compact, /memory, etc."""

from kitten_cli.commands.registry import (
    SlashCommandRegistry,
    CommandResult,
    CommandResultType,
    CommandDefinition,
)
from kitten_cli.commands.builtins import create_default_registry, register_builtin_commands

__all__ = [
    "SlashCommandRegistry",
    "CommandResult",
    "CommandResultType",
    "CommandDefinition",
    "create_default_registry",
    "register_builtin_commands",
]
