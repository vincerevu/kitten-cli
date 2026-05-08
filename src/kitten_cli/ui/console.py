"""
Console output utilities — Rich-based rendering for terminal output.
Ref: gemini-cli/packages/core/src/output/outputManager.ts
"""
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme

# Custom theme matching kitten-cli branding
KITTEN_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "tool_name": "bold magenta",
    "tool_args": "dim",
    "thinking": "dim italic",
    "user": "bold blue",
    "assistant": "bold green",
})

# Shared console instance
_console: Optional[Console] = None


def get_console() -> Console:
    """Get or create the shared Rich console."""
    global _console
    if _console is None:
        _console = Console(theme=KITTEN_THEME, highlight=False)
    return _console


def print_markdown(text: str) -> None:
    """Print markdown-formatted text."""
    get_console().print(Markdown(text))


def print_error(message: str) -> None:
    """Print an error message."""
    get_console().print(f"[error]✗ {message}[/error]")


def print_success(message: str) -> None:
    """Print a success message."""
    get_console().print(f"[success]✓ {message}[/success]")


def print_info(message: str) -> None:
    """Print an info message."""
    get_console().print(f"[info]ℹ {message}[/info]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    get_console().print(f"[warning]⚠ {message}[/warning]")


def print_tool_call(tool_name: str, args_summary: str = "") -> None:
    """Print a tool call indicator."""
    suffix = f" [tool_args]{args_summary}[/tool_args]" if args_summary else ""
    get_console().print(f"[tool_name]⚡ {tool_name}[/tool_name]{suffix}")


def print_code(code: str, language: str = "python") -> None:
    """Print syntax-highlighted code."""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    get_console().print(syntax)


def print_panel(content: str, title: str = "", border_style: str = "cyan") -> None:
    """Print content in a bordered panel."""
    get_console().print(Panel(content, title=title, border_style=border_style))


def print_thinking(text: str) -> None:
    """Print model thinking/reasoning text."""
    get_console().print(f"[thinking]{text}[/thinking]")
