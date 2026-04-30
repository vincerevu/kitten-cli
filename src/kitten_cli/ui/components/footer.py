from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult

class AppFooter(Widget):
    """The application footer containing status and tips."""

    def compose(self) -> ComposeResult:
        yield Static("💡 Tip: Use /help to see all available commands.", classes="footer-text")
