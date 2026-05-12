import os
from typing import Optional, List
from kitten_cli.prompts.snippets import PromptOptions, get_core_system_prompt
from kitten_cli.tools.registry import ToolRegistry
# Note: config system is not fully implemented yet, so we use duck typing for config

class PromptProvider:
    def __init__(self, tool_registry: ToolRegistry, config=None):
        self.tool_registry = tool_registry
        self.config = config

    def get_core_system_prompt(
        self,
        interactive_override: Optional[bool] = None,
        memory: Optional[str] = None
    ) -> str:
        """
        Generates the core system prompt based on config and available tools.
        """
        # Determine interactive mode
        interactive_mode = True
        if interactive_override is not None:
            interactive_mode = interactive_override
        elif self.config and hasattr(self.config, 'is_interactive'):
            interactive_mode = self.config.is_interactive()

        # Determine approval mode
        approval_mode = "DEFAULT"
        if self.config and hasattr(self.config, 'approval_mode'):
            approval_mode = self.config.approval_mode

        # Gather tools
        tool_names = self.tool_registry.get_names()

        # Workspace
        workspace_path = os.getcwd()
        if self.config and hasattr(self.config, 'workspace_path'):
            workspace_path = self.config.workspace_path

        # Assemble options
        options = PromptOptions(
            interactive=interactive_mode,
            approval_mode=approval_mode,
            os_info=True,
            workspace_path=workspace_path,
            tools_list=tool_names,
            memory_context=memory
        )

        return get_core_system_prompt(options)
