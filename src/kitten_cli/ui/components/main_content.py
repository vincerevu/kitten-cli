from textual.widget import Widget
from textual.widgets import Static
from textual.containers import VerticalScroll
from textual.app import ComposeResult

class MainContent(Widget):
    """The main content area displaying the chat history (ScrollableList in Gemini)."""

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="chat-history"):
            yield Static("🤖 Hello! I am your AI coding assistant. How can I help you today?", classes="chat-message ai-message")
            yield Static("👤 I need to write a python script.", classes="chat-message user-message")
            yield Static("🤖 Sure! Let's get started.", classes="chat-message ai-message")
