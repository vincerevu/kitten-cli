from textual.widget import Widget
from textual.widgets import Label
from textual.app import ComposeResult
from textual.containers import Horizontal

class StatusDisplay(Widget):
    """Mapped from StatusDisplay.tsx. Displays context summary."""
    
    DEFAULT_CSS = """
    StatusDisplay {
        height: 1;
        width: 100%;
        background: $panel;
        color: $text-muted;
    }
    .status-item {
        margin-right: 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            # These values will later be bound to the global UI state
            yield Label("📁 Context: 0 files", classes="status-item")
            yield Label("🔌 MCP Servers: 0", classes="status-item")
            yield Label("🛠️ Skills: 0", classes="status-item")
            yield Label("⚙️ Background: 0", classes="status-item")
