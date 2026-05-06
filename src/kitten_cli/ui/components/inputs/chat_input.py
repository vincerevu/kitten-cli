from textual.widget import Widget
from textual.widgets import TextArea
from textual.app import ComposeResult
from textual.message import Message

class ChatInput(Widget):
    """Mapped from Composer.tsx / MultiLineInput.tsx. 
    Handles multiline text input for chatting with the AI.
    """
    
    class Submitted(Message):
        """Emitted when the user submits a message."""
        def __init__(self, text: str) -> None:
            self.text = text
            super().__init__()
            
    DEFAULT_CSS = """
    ChatInput {
        height: auto;
        max-height: 10;
        border: solid $primary;
        padding: 0 1;
        margin: 1 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        # A simple multiline text area
        text_area = TextArea(language="markdown", id="composer-text-area")
        text_area.show_line_numbers = False
        yield text_area

    def on_key(self, event) -> None:
        if event.key == "enter":
            text_area = self.query_one("#composer-text-area", TextArea)
            text = text_area.text.strip()
            if text:
                self.post_message(self.Submitted(text))
                text_area.text = ""
                # Prevent the enter key from adding a newline
                event.prevent_default()
