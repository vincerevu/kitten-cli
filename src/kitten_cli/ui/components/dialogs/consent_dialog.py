from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Markdown, Button

class ConsentDialog(ModalScreen[bool]):
    """A dialog to ask the user for consent (e.g. Terms, file modifications)."""
    
    DEFAULT_CSS = """
    ConsentDialog {
        align: center middle;
        background: $background 50%;
    }
    
    #consent-container {
        width: 80;
        height: 20;
        padding: 1 2;
        background: $surface;
        border: thick $warning;
    }
    
    .dialog-buttons {
        height: auto;
        align: right middle;
        margin-top: 1;
    }
    """
    
    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self.content = content

    def compose(self) -> ComposeResult:
        with Vertical(id="consent-container"):
            yield Markdown(self.content)
            
            with Horizontal(classes="dialog-buttons"):
                yield Button("Decline", variant="error", id="decline")
                yield Button("Agree", variant="success", id="agree")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "agree":
            self.dismiss(True)
        else:
            self.dismiss(False)
