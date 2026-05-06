"""
Tools package — all built-in tools for kitten-cli.
"""
from kitten_cli.tools.registry import ToolRegistry
from kitten_cli.tools.read_file import ReadFileTool
from kitten_cli.tools.write_file import WriteFileTool
from kitten_cli.tools.edit import EditTool
from kitten_cli.tools.shell import ShellTool
from kitten_cli.tools.ls import LSTool
from kitten_cli.tools.grep import GrepTool
from kitten_cli.tools.glob import GlobTool
from kitten_cli.tools.web_fetch import WebFetchTool
from kitten_cli.tools.web_search import WebSearchTool
from kitten_cli.tools.ask_user import AskUserTool
from kitten_cli.tools.memory_tool import MemoryTool
from kitten_cli.tools.complete_task import CompleteTaskTool
from kitten_cli.tools.read_many_files import ReadManyFilesTool


def create_default_registry(workspace_root: str = "") -> ToolRegistry:
    """Create a ToolRegistry with all default tools registered."""
    registry = ToolRegistry()

    shell_tool = ShellTool()
    if workspace_root:
        shell_tool.set_default_cwd(workspace_root)

    memory_tool = MemoryTool()
    if workspace_root:
        memory_tool.set_workspace_root(workspace_root)

    registry.register(ReadFileTool())
    registry.register(ReadManyFilesTool())
    registry.register(WriteFileTool())
    registry.register(EditTool())
    registry.register(shell_tool)
    registry.register(LSTool())
    registry.register(GrepTool())
    registry.register(GlobTool())
    registry.register(WebFetchTool())
    registry.register(WebSearchTool())
    registry.register(AskUserTool())
    registry.register(memory_tool)
    registry.register(CompleteTaskTool())

    return registry
