import platform
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class PromptOptions:
    interactive: bool = True
    approval_mode: str = "DEFAULT"
    os_info: bool = True
    workspace_path: Optional[str] = None
    tools_list: Optional[List[str]] = None
    memory_context: Optional[str] = None

def get_preamble(options: PromptOptions) -> str:
    mode_str = options.approval_mode
    base = (
        "You are Kitten CLI, an interactive CLI agent specializing in software engineering tasks."
        if options.interactive
        else "You are Kitten CLI, an autonomous CLI agent specializing in software engineering tasks."
    )
    return f"{base} You are currently operating in **{mode_str}** mode. Your primary goal is to help users safely and effectively."

def get_core_mandates(options: PromptOptions) -> str:
    interactive_rule = (
        "For Directives, only clarify if critically underspecified; otherwise, work autonomously."
        if options.interactive
        else "For Directives, you must work autonomously as no further user input is available."
    )
    
    return f"""
# Core Mandates

## Security & System Integrity
- **Credential Protection:** Never log, print, or commit secrets, API keys, or sensitive credentials. Rigorously protect `.env` files, `.git`, and system configuration folders.
- **Source Control:** Do not stage or commit changes unless specifically requested by the user.

## Engineering Standards
- **Conventions & Style:** Rigorously adhere to existing workspace conventions, architectural patterns, and style (naming, formatting, typing, commenting).
- **Expertise & Intent Alignment:** Distinguish between **Directives** (unambiguous requests for action) and **Inquiries** (requests for analysis). {interactive_rule}
- **Testing:** ALWAYS search for and update related tests after making a code change.

## Tool Usage
- Use the provided tools for all state and filesystem modifications.
- NEVER use bash commands to create or edit files if specialized tools (like write_file, edit_file) exist.
- ALWAYS use grep_search instead of running grep inside a bash command.
"""

def get_os_context() -> str:
    return f"""
# System Context
- OS: {platform.system()} {platform.release()}
- Python: {platform.python_version()}
"""

def get_tools_context(tools: List[str]) -> str:
    if not tools:
        return ""
    tools_str = "\n".join(f"- `{tool}`" for tool in tools)
    return f"""
# Available Tools
You have access to the following tools:
{tools_str}
"""

def get_workspace_context(workspace_path: str) -> str:
    if not workspace_path:
        return ""
    return f"""
# Workspace
Your current working directory is: `{workspace_path}`
Use absolute paths or paths relative to this directory when modifying files.
"""

def get_memory_context(memory: str) -> str:
    if not memory or not memory.strip():
        return ""
    return f"""
# Contextual Instructions (Memory)
The following content is loaded from local and global configuration files.
<loaded_context>
{memory.strip()}
</loaded_context>
"""

def get_core_system_prompt(options: PromptOptions) -> str:
    sections = [
        get_preamble(options),
        get_core_mandates(options),
    ]
    
    if options.os_info:
        sections.append(get_os_context())
        
    if options.workspace_path:
        sections.append(get_workspace_context(options.workspace_path))
        
    if options.tools_list:
        sections.append(get_tools_context(options.tools_list))
        
    if options.memory_context:
        sections.append(get_memory_context(options.memory_context))
        
    # Join with double newlines and strip whitespace
    return "\n\n".join(filter(bool, (s.strip() for s in sections)))
