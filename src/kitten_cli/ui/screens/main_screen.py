from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Vertical
from kitten_cli.ui.components.header import AppHeader
from kitten_cli.ui.components.main_content import MainContent
from kitten_cli.ui.components.inputs.chat_input import ChatInput
from kitten_cli.ui.components.inputs.suggestions import Suggestions
from kitten_cli.ui.components.footer import AppFooter

class MainScreen(Screen):
    """The main screen layout containing Header, Content, Inputs, and Footer."""

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield MainContent()
        yield Suggestions()
        yield ChatInput()
        yield AppFooter()
