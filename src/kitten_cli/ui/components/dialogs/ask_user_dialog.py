from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, Input

class AskUserDialog(ModalScreen[bool]):
    """A dialog to ask the user a question or for permission."""
    
    DEFAULT_CSS = """
    AskUserDialog {
        align: center middle;
        background: $background 50%;
    }
    
    #ask-dialog-container {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
    }
    
    .dialog-buttons {
        height: auto;
        align: right middle;
        margin-top: 1;
    }
    
    .dialog-button {
        margin-left: 1;
    }
    """
    
    def __init__(self, question: str, **kwargs):
        super().__init__(**kwargs)
        self.question = question

    def compose(self) -> ComposeResult:
        with Vertical(id="ask-dialog-container"):
            yield Label(self.question, id="ask-question-label")
            yield Input(placeholder="Type your answer here...", id="ask-input")
            
            with Horizontal(classes="dialog-buttons"):
                yield Button("Cancel", variant="error", id="cancel", classes="dialog-button")
                yield Button("Submit", variant="success", id="submit", classes="dialog-button")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.dismiss(True)
        else:
            self.dismiss(False)
