from textual.app import App, ComposeResult
from textual.binding import Binding
from textual import work
from typing import Optional

from kitten_cli.ui.screens.main_screen import MainScreen
from kitten_cli.ui.styles.colors import gemini_dark_theme
from kitten_cli.agents.executor import AgentExecutor, AgentEvent, AgentEventType
from kitten_cli.core.state import SessionState
from kitten_cli.config.manager import ConfigManager
from kitten_cli.ui.components.dialogs.confirmation_dialog import ToolConfirmationDialog, ConfirmationResult


class KittenUI(App):
    """
    The main Textual application for Kitten CLI.
    Runs the agent loop and dispatches events to the UI.
    """

    CSS_PATH = "styles/main.tcss"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("ctrl+o", "toggle_expand", "Expand", show=True)
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_theme(gemini_dark_theme)
        self.theme = "gemini-dark"
        
        # Initialize Agent State
        self.config_manager = ConfigManager()
        self.session_state = SessionState()
        self.executor = AgentExecutor(self.session_state, self.config_manager)
        
        # Track active turn worker
        self.active_turn = None

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

    @work(exclusive=True)
    async def run_agent_turn(self) -> None:
        """Run the agent loop until it finishes a turn."""
        main_screen = self.screen
        if not isinstance(main_screen, MainScreen):
            return

        try:
            async for event in self.executor.run():
                # Dispatch event to the main screen for rendering
                self.call_from_thread(main_screen.handle_agent_event, event)
                
                # Handle tool confirmation natively
                if event.type == AgentEventType.CONFIRMATION_REQUEST:
                    await self._handle_confirmation(event)
                    
        except Exception as e:
            import traceback
            err_msg = f"Fatal Error: {str(e)}\n{traceback.format_exc()}"
            self.call_from_thread(main_screen.handle_error, err_msg)
            
    async def _handle_confirmation(self, event: AgentEvent) -> None:
        """Present the confirmation dialog and pause execution."""
        tool_name = event.data.get("tool_name", "unknown")
        tool_args = event.data.get("tool_args", {})
        callback = event.data.get("response_callback")
        
        if not callback:
            return

        # Show modal dialog and wait for result
        dialog = ToolConfirmationDialog(tool_name, tool_args)
        
        # We must push the screen from the main thread
        def on_dialog_dismissed(result: Optional[ConfirmationResult]) -> None:
            if result:
                callback(result.action)
            else:
                callback("reject")  # Default to reject if dismissed

        self.call_from_thread(self.push_screen, dialog, on_dialog_dismissed)

if __name__ == "__main__":
    app = KittenUI()
    app.run()
