import sys
import os

# Ensure we can import kitten_cli
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from kitten_cli.prompts import PromptProvider
from kitten_cli.tools.registry import ToolRegistry
from kitten_cli.tools.shell import ShellTool
from kitten_cli.tools.read_file import ReadFileTool
from kitten_cli.tools.write_file import WriteFileTool

# Mock config
class MockConfig:
    def __init__(self):
        self.approval_mode = "DEFAULT"
        self.workspace_path = os.getcwd()
    
    def is_interactive(self):
        return True

def main():
    registry = ToolRegistry()
    registry.register(ShellTool())
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())

    config = MockConfig()
    provider = PromptProvider(tool_registry=registry, config=config)

    print("=== System Prompt (Interactive) ===\n")
    prompt = provider.get_core_system_prompt(memory="Don't use Python 2. Use python 3 only.")
    print(prompt)

    print("\n\n=== System Prompt (Non-Interactive, PLAN mode) ===\n")
    config.approval_mode = "PLAN"
    prompt2 = provider.get_core_system_prompt(interactive_override=False)
    print(prompt2)

if __name__ == "__main__":
    main()
