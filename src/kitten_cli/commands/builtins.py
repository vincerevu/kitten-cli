"""
Built-in slash commands.
These are registered by default when the agent starts.
"""

from kitten_cli.commands.registry import CommandResult, CommandResultType, SlashCommandRegistry


def register_builtin_commands(registry: SlashCommandRegistry) -> None:
    """Register all built-in slash commands."""

    # /help
    def cmd_help(args: str) -> CommandResult:
        commands = registry.list_commands()
        lines = ["Available commands:", ""]
        for cmd in commands:
            aliases = f" (aliases: {', '.join('/' + a for a in cmd.aliases)})" if cmd.aliases else ""
            usage = f"  Usage: /{cmd.name} {cmd.usage}" if cmd.usage else ""
            lines.append(f"  /{cmd.name} — {cmd.description}{aliases}")
            if usage:
                lines.append(usage)
        return CommandResult(content="\n".join(lines))

    registry.register(
        "help", "Show available slash commands",
        cmd_help, aliases=["h", "?"],
    )

    # /clear
    def cmd_clear(args: str) -> CommandResult:
        return CommandResult(
            type=CommandResultType.LOAD_HISTORY,
            content="Conversation cleared.",
        )

    registry.register(
        "clear", "Clear conversation history",
        cmd_clear, aliases=["reset"],
    )

    # /compact
    def cmd_compact(args: str) -> CommandResult:
        return CommandResult(
            type=CommandResultType.SUBMIT_PROMPT,
            content="[System: Compact the conversation context now. Summarize key context and discard verbose details.]",
        )

    registry.register(
        "compact", "Trigger context compaction",
        cmd_compact, aliases=["compress"],
    )

    # /status
    def cmd_status(args: str) -> CommandResult:
        # This is a placeholder — the actual implementation will be wired
        # to the agent executor to get real stats.
        return CommandResult(
            content="Status: Use the agent executor to get real-time stats.",
        )

    registry.register(
        "status", "Show agent status (turns, tokens)",
        cmd_status, aliases=["stats"],
    )

    # /config
    def cmd_config(args: str) -> CommandResult:
        from kitten_cli.config import resolve_config
        cfg = resolve_config()
        lines = [
            "Current configuration:",
            f"  Model: {cfg.model}",
            f"  Temperature: {cfg.temperature}",
            f"  Max turns: {cfg.max_turns}",
            f"  Max output tokens: {cfg.max_output_tokens}",
            f"  Theme: {cfg.theme}",
            f"  Sandbox: {cfg.sandbox}",
        ]
        return CommandResult(content="\n".join(lines))

    registry.register(
        "config", "Show current configuration",
        cmd_config, aliases=["cfg"],
    )

    # /memory
    def cmd_memory(args: str) -> CommandResult:
        from kitten_cli.services.memory_service import MemoryService
        svc = MemoryService()

        if args.strip() == "list" or not args.strip():
            files = svc.discover_memory_files()
            if not files:
                return CommandResult(content="No KITTEN.md memory files found.")
            lines = ["Memory files:"]
            for f in files:
                content = svc.load_memory(f)
                lines.append(f"  {f} ({len(content)} chars)")
            return CommandResult(content="\n".join(lines))

        elif args.strip() == "show":
            content = svc.load_all_memory()
            if not content:
                return CommandResult(content="No memory content found.")
            return CommandResult(content=content)

        else:
            return CommandResult(
                content="Usage: /memory [list|show]",
                message_type="info",
            )

    registry.register(
        "memory", "View KITTEN.md memory files",
        cmd_memory, usage="[list|show]",
    )

    # /undo
    def cmd_undo(args: str) -> CommandResult:
        return CommandResult(
            type=CommandResultType.TOOL,
            content="Triggering undo via git checkpoint restore.",
            tool_name="undo",
            tool_args={},
        )

    registry.register(
        "undo", "Restore last checkpoint",
        cmd_undo,
    )

    # /quit
    def cmd_quit(args: str) -> CommandResult:
        return CommandResult(
            content="__QUIT__",
            message_type="info",
        )

    registry.register(
        "quit", "Exit the agent",
        cmd_quit, aliases=["exit", "q"],
    )


def create_default_registry() -> SlashCommandRegistry:
    """Create a registry with all built-in commands."""
    registry = SlashCommandRegistry()
    register_builtin_commands(registry)
    return registry
