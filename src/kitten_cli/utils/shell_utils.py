
import platform
import re
import shlex
from typing import List, Optional, Tuple


def get_shell_info() -> dict:
    """Get the current shell information."""
    system = platform.system()
    if system == "Windows":
        return {
            "os": "windows",
            "shell": "powershell",
            "shell_cmd": ["powershell", "-NoProfile", "-Command"],
        }
    else:
        return {
            "os": "linux" if system == "Linux" else "darwin",
            "shell": "bash",
            "shell_cmd": ["/bin/bash", "-c"],
        }


def extract_root_command(command: str) -> str:
    """Extract the root command from a command string (e.g. 'git commit -m msg' → 'git')."""
    command = command.strip()
    # Handle common prefixes
    for prefix in ("sudo ", "env ", "time "):
        if command.startswith(prefix):
            command = command[len(prefix):].strip()

    # Split and take first word
    parts = command.split(None, 1)
    return parts[0] if parts else ""


def extract_all_commands(command: str) -> List[str]:
    """Extract all commands from a compound command (;, &&, ||, |)."""
    # Split by command separators
    commands = re.split(r'\s*(?:&&|\|\||;|\|)\s*', command)
    return [extract_root_command(cmd) for cmd in commands if cmd.strip()]


def has_redirection(command: str) -> bool:
    """Check if a command contains output redirection."""
    # Simple check for >, >>, 2>, etc.
    return bool(re.search(r'(?<!\w)[12]?>>?\s', command))


def is_interactive_command(command: str) -> bool:
    """Check if a command is likely interactive (needs TTY)."""
    root = extract_root_command(command)
    interactive_commands = {
        "vim", "vi", "nano", "emacs", "less", "more", "top", "htop",
        "man", "ssh", "telnet", "ftp", "python", "python3", "node",
        "irb", "rails", "pry",
    }
    return root in interactive_commands


def sanitize_for_display(command: str, max_len: int = 120) -> str:
    """Sanitize a command for safe display (hide sensitive args)."""
    # Hide common secrets
    sanitized = re.sub(
        r'((?:password|token|secret|key|api_key)\s*=\s*)\S+',
        r'\1***',
        command,
        flags=re.IGNORECASE,
    )
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len] + "..."
    return sanitized
