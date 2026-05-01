from textual.widget import Widget
from textual.widgets import Input
from textual.app import ComposeResult

class ShellInput(Widget):
    """Handles single-line shell commands, prefixed by $ or similar."""
    
    DEFAULT_CSS = """
    ShellInput {
        height: 3;
        margin: 1 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter shell command...", id="shell-input")
