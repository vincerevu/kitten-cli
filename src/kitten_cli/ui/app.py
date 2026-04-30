from textual.app import App, ComposeResult
from textual.binding import Binding
from kitten_cli.ui.screens.main_screen import MainScreen

class KittenUI(App):
    """The main Textual application for Kitten CLI."""

    CSS_PATH = "styles/main.tcss"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+o", "toggle_expand", "Expand", show=True)
    ]

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

if __name__ == "__main__":
    app = KittenUI()
    app.run()
