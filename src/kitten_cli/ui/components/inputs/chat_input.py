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
        border: none;
        padding: 0;
        margin: 0;
        background: transparent;
    }
    
    #hints-container {
        height: 1;
        layout: horizontal;
    }
    
    #hint-left {
        color: gray;
        width: 1fr;
        text-align: left;
    }
    
    TextArea {
        background: #333333 !important;
        color: white;
        border: none !important;
        height: auto;
        min-height: 1;
        max-height: 8;
        padding: 0;
        width: 1fr;
    }
    
    TextArea:focus {
        background: #333333 !important;
        border: none !important;
    }
    
    #input-row {
        height: auto;
        layout: horizontal;
        background: #333333;
    }
    
    #input-prompt {
        width: 2;
        background: #333333;
        color: magenta;
        padding-left: 0;
        text-style: bold;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(id="hints-container"):
                yield Static("Shift+Tab to accept edits", id="hint-left")
                
            # A simple multiline text area
            with Horizontal(id="input-row"):
                yield Static("> ", id="input-prompt")
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
