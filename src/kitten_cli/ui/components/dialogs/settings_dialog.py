from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, Switch

class SettingsDialog(ModalScreen[None]):
    """A dialog to configure application settings."""
    
    DEFAULT_CSS = """
    SettingsDialog {
        align: center middle;
        background: $background 50%;
    }
    
    #settings-container {
        width: 70;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $accent;
    }
    
    .setting-row {
        height: 3;
        align: space-between middle;
        margin-bottom: 1;
    }
    
    .dialog-buttons {
        height: auto;
        align: right middle;
        margin-top: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical(id="settings-container"):
            yield Label("⚙️ Settings", classes="text-bold")
            
            with Horizontal(classes="setting-row"):
                yield Label("Enable Dark Mode")
                yield Switch(value=True)
                
            with Horizontal(classes="setting-row"):
                yield Label("Show Context Summary")
                yield Switch(value=True)
                
            with Horizontal(classes="dialog-buttons"):
                yield Button("Close", variant="primary", id="close")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.dismiss(None)
