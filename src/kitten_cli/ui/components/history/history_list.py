from textual.widget import Widget
from textual.containers import VerticalScroll
from textual.app import ComposeResult
from typing import List, Dict, Any
from .message_bubble import MessageBubble

class HistoryList(Widget):
    """A scrollable list of message bubbles.
    Mapped from ScrollableList / HistoryItemDisplay mapping.
    """
    
    DEFAULT_CSS = """
    HistoryList {
        height: auto;
        width: 100%;
    }
    #chat-history-scroll {
        height: auto;
    }
    """
    
    def __init__(self, history: List[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        # Default mock history for preview purposes
        self.history = history or [
            {"type": "gemini", "text": "Hello! I am **Kitten CLI**. How can I assist you today?"},
            {"type": "user", "text": "Please write a simple python script."},
            {"type": "gemini", "text": "Certainly! Here is a simple script:\n```python\nprint('Meow!')\n```"}
        ]
        
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="chat-history-scroll"):
            for item in self.history:
                yield MessageBubble(item)
