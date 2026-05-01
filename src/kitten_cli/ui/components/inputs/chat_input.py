from textual.widget import Widget
from textual.widgets import TextArea
from textual.app import ComposeResult

class ChatInput(Widget):
    """Mapped from Composer.tsx / MultiLineInput.tsx. 
    Handles multiline text input for chatting with the AI.
    """
    
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
        text_area = TextArea(language="markdown")
        text_area.show_line_numbers = False
        yield text_area
