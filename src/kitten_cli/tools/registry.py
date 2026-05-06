"""
Tool Registry — Manages all available tools.
Ref: gemini-cli/packages/core/src/tools/tool-registry.ts
"""
from typing import Any, Dict, List, Optional
from kitten_cli.tools.base import DeclarativeTool


class ToolRegistry:
    """Registry of all available tools for the agent."""

    def __init__(self):
        self._tools: Dict[str, DeclarativeTool] = {}

    def register(self, tool: DeclarativeTool) -> None:
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def get(self, name: str) -> Optional[DeclarativeTool]:
        return self._tools.get(name)

    def get_all(self) -> List[DeclarativeTool]:
        return list(self._tools.values())

    def get_schemas(self) -> List[Dict[str, Any]]:
        """Return all tool schemas for LLM function calling."""
        return [tool.schema for tool in self._tools.values()]

    def get_names(self) -> List[str]:
        return list(self._tools.keys())

    def has(self, name: str) -> bool:
        return name in self._tools

    def count(self) -> int:
        return len(self._tools)
