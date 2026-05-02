from textual.widget import Widget
from textual.app import ComposeResult
from kitten_cli.ui.components.history.history_list import HistoryList

class MainContent(Widget):
    """The main content area displaying the chat history (ScrollableList in Gemini)."""

    def compose(self) -> ComposeResult:
        yield HistoryList()
