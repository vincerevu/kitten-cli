from textual.app import App, ComposeResult
from textual.binding import Binding
from kitten_cli.ui.screens.main_screen import MainScreen
from kitten_cli.ui.styles.colors import gemini_dark_theme

class KittenUI(App):
    """The main Textual application for Kitten CLI."""

    CSS_PATH = "styles/main.tcss"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+o", "toggle_expand", "Expand", show=True)
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_theme(gemini_dark_theme)
        self.theme = "gemini-dark"

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

if __name__ == "__main__":
    app = KittenUI()
    app.run()
