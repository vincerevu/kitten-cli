from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, Button, Input
from kitten_cli.config.manager import ConfigManager

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
        height: auto;
        margin-bottom: 1;
    }
    
    .setting-label {
        width: 100%;
        margin-bottom: 1;
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
    
    def on_mount(self) -> None:
        self.config = ConfigManager.load_config()
        self.query_one("#model-input", Input).value = self.config.llm.model
        self.query_one("#api-key-input", Input).value = self.config.llm.api_key or ""
        self.query_one("#base-url-input", Input).value = self.config.llm.base_url or ""
    
    def compose(self) -> ComposeResult:
        with Vertical(id="settings-container"):
            yield Label("⚙️ Model Settings", classes="text-bold")
            
            with Vertical(classes="setting-row"):
                yield Label("Model (LiteLLM format)", classes="setting-label")
                yield Input(placeholder="e.g. gemini/gemini-1.5-pro", id="model-input")
                
            with Vertical(classes="setting-row"):
                yield Label("API Key", classes="setting-label")
                yield Input(placeholder="sk-...", password=True, id="api-key-input")
                
            with Vertical(classes="setting-row"):
                yield Label("Base URL (Optional)", classes="setting-label")
                yield Input(placeholder="http://localhost:11434", id="base-url-input")
                
            with Horizontal(classes="dialog-buttons"):
                yield Button("Cancel", variant="error", id="cancel", classes="dialog-button")
                yield Button("Save", variant="success", id="save", classes="dialog-button")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.config.llm.model = self.query_one("#model-input", Input).value
            
            api_key = self.query_one("#api-key-input", Input).value
            self.config.llm.api_key = api_key if api_key else None
            
            base_url = self.query_one("#base-url-input", Input).value
            self.config.llm.base_url = base_url if base_url else None
            
            ConfigManager.save_config(self.config)
            self.dismiss(None)
        else:
            self.dismiss(None)
