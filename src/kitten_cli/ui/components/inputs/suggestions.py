from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Horizontal
from textual.app import ComposeResult
from typing import List

class Suggestions(Widget):
    """Mapped from SuggestionsDisplay.tsx. Displays clickable/selectable suggestions."""
    
    DEFAULT_CSS = """
    Suggestions {
        height: 3;
        margin: 0 2;
        padding: 0 1;
        background: $surface;
    }
    .suggestion-item {
        padding: 0 1;
        margin-right: 1;
        background: $primary;
        color: $text;
        border: solid $primary-darken-1;
    }
    """
    
    def __init__(self, suggestions: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.suggestions = suggestions or ["/help", "/clear", "/context"]
        
    def compose(self) -> ComposeResult:
        with Horizontal():
            for suggestion in self.suggestions:
                yield Static(suggestion, classes="suggestion-item")
