"""
Slash command system — handles /commands in user input.
Ref: gemini-cli/packages/core/src/commands/

Slash commands are shortcuts that execute actions without going through the LLM:
  /help     — Show available commands
  /clear    — Clear conversation history
  /compact  — Trigger context compaction
  /memory   — View/edit KITTEN.md memory files
  /status   — Show agent status (turns, tokens, etc.)
  /undo     — Restore last checkpoint
  /config   — Show current config
  /quit     — Exit the agent
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class CommandResultType(str, Enum):
    """Type of result a command produces."""
    MESSAGE = "message"         # Display a message to the user
    TOOL = "tool"               # Trigger a tool call
    SUBMIT_PROMPT = "submit"    # Submit content as a prompt to the LLM
    LOAD_HISTORY = "history"    # Replace conversation history


@dataclass
class CommandResult:
    """Result of executing a slash command."""
    type: CommandResultType = CommandResultType.MESSAGE
    content: str = ""
    message_type: str = "info"  # "info" | "error" | "warning"
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None


@dataclass
class CommandDefinition:
    """Definition of a slash command."""
    name: str                   # Command name without /
    description: str
    usage: str = ""             # Usage example
    aliases: List[str] = None   # Alternative names

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class SlashCommandRegistry:
    """
    Registry for slash commands.
    Commands are registered with a handler function and can be dispatched by name.
    """

    def __init__(self):
        self._commands: Dict[str, CommandDefinition] = {}
        self._handlers: Dict[str, Callable] = {}
        self._aliases: Dict[str, str] = {}  # alias -> canonical name

    def register(
        self,
        name: str,
        description: str,
        handler: Callable,
        usage: str = "",
        aliases: Optional[List[str]] = None,
    ) -> None:
        """Register a slash command."""
        defn = CommandDefinition(
            name=name,
            description=description,
            usage=usage,
            aliases=aliases or [],
        )
        self._commands[name] = defn
        self._handlers[name] = handler

        for alias in defn.aliases:
            self._aliases[alias] = name

    def get_command(self, name: str) -> Optional[CommandDefinition]:
        """Get a command definition by name or alias."""
        # Direct match
        if name in self._commands:
            return self._commands[name]
        # Alias match
        canonical = self._aliases.get(name)
        if canonical:
            return self._commands.get(canonical)
        return None

    def execute(self, name: str, args: str = "") -> CommandResult:
        """Execute a slash command by name."""
        # Resolve alias
        canonical = self._aliases.get(name, name)
        handler = self._handlers.get(canonical)

        if not handler:
            return CommandResult(
                type=CommandResultType.MESSAGE,
                content=f"Unknown command: /{name}. Type /help for available commands.",
                message_type="error",
            )

        try:
            result = handler(args)
            if isinstance(result, CommandResult):
                return result
            if isinstance(result, str):
                return CommandResult(content=result)
            return CommandResult(content=str(result))
        except Exception as ex:
            return CommandResult(
                type=CommandResultType.MESSAGE,
                content=f"Command error: {ex}",
                message_type="error",
            )

    def list_commands(self) -> List[CommandDefinition]:
        """List all registered commands."""
        return sorted(self._commands.values(), key=lambda c: c.name)

    @staticmethod
    def is_slash_command(text: str) -> bool:
        """Check if input text is a slash command."""
        return text.strip().startswith("/")

    @staticmethod
    def parse_command(text: str) -> tuple:
        """Parse slash command text into (name, args)."""
        stripped = text.strip()
        if not stripped.startswith("/"):
            return ("", stripped)

        parts = stripped[1:].split(None, 1)
        name = parts[0] if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        return (name, args)
