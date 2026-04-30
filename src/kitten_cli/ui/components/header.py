from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult

ASCII_LOGO = r"""
 /\_/\  
( o.o ) Kitten CLI
 > ^ < 
"""

class AppHeader(Widget):
    """The application header containing the ASCII logo."""

    def compose(self) -> ComposeResult:
        yield Static(ASCII_LOGO, classes="header-logo")
