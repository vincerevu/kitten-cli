from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class DiscoveredPrompt:
    name: str
    description: Optional[str] = None
    server_name: Optional[str] = None
    # Add other fields as needed (e.g. arguments, execution logic)

class PromptRegistry:
    def __init__(self):
        self._prompts: Dict[str, DiscoveredPrompt] = {}

    def register_prompt(self, prompt: DiscoveredPrompt) -> None:
        """Registers a prompt definition."""
        if prompt.name in self._prompts:
            if prompt.server_name:
                new_name = f"{prompt.server_name}_{prompt.name}"
                # TODO: use logger
                print(f"Warning: Prompt with name '{prompt.name}' is already registered. Renaming to '{new_name}'.")
                prompt.name = new_name
                self._prompts[new_name] = prompt
            else:
                self._prompts[prompt.name] = prompt
        else:
            self._prompts[prompt.name] = prompt

    def get_all_prompts(self) -> List[DiscoveredPrompt]:
        """Returns a list of all registered prompts, sorted by name."""
        return sorted(list(self._prompts.values()), key=lambda p: p.name)

    def get_prompt(self, name: str) -> Optional[DiscoveredPrompt]:
        """Get the definition of a specific prompt."""
        return self._prompts.get(name)

    def get_prompts_by_server(self, server_name: str) -> List[DiscoveredPrompt]:
        """Returns a list of prompts registered from a specific MCP server."""
        server_prompts = [p for p in self._prompts.values() if p.server_name == server_name]
        return sorted(server_prompts, key=lambda p: p.name)

    def clear(self) -> None:
        """Clears all the prompts from the registry."""
        self._prompts.clear()

    def remove_prompts_by_server(self, server_name: str) -> None:
        """Removes all prompts from a specific server."""
        keys_to_remove = [name for name, prompt in self._prompts.items() if prompt.server_name == server_name]
        for key in keys_to_remove:
            del self._prompts[key]
