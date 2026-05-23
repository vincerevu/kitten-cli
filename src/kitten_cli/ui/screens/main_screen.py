from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Vertical
from textual import work

from kitten_cli.ui.components.header import AppHeader
from kitten_cli.ui.components.main_content import MainContent
from kitten_cli.ui.components.inputs.chat_input import ChatInput
from kitten_cli.ui.components.inputs.suggestions import Suggestions
from kitten_cli.ui.components.footer import AppFooter
from kitten_cli.ui.components.history.history_list import HistoryList
from kitten_cli.ui.components.history.message_bubble import MessageBubble

from kitten_cli.agents.executor import AgentEvent, AgentEventType
from kitten_cli.core.types import Message, Role
from kitten_cli.commands.registry import SlashCommandRegistry
from kitten_cli.commands.builtins import create_default_registry


class MainScreen(Screen):
    """The main screen layout containing Header, Content, Inputs, and Footer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_ai_bubble = None
        self.current_ai_text = ""
        self.command_registry = create_default_registry()

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield MainContent()
        yield Suggestions()
        yield ChatInput()
        yield AppFooter()
        
    def on_chat_input_submitted(self, event: ChatInput.Submitted) -> None:
        user_message = event.text.strip()
        if not user_message:
            return
            
        history_list = self.query_one(HistoryList)
        
        # Check if it's a slash command
        if self.command_registry.is_slash_command(user_message):
            name, args = self.command_registry.parse_command(user_message)
            result = self.command_registry.execute(name, args)
            
            # Show user command
            history_list.query_one("#chat-history-scroll").mount(
                MessageBubble({"type": "user", "text": user_message})
            )
            
            # Show command result
            if result.content:
                if result.content == "__QUIT__":
                    self.app.exit()
                    return
                    
                msg_type = "error" if result.message_type == "error" else "system"
                history_list.query_one("#chat-history-scroll").mount(
                    MessageBubble({"type": msg_type, "text": result.content})
                )
            
            history_list.query_one("#chat-history-scroll").scroll_end(animate=False)
            
            # If it triggered a tool call or prompt submission, we'd handle it here
            # (Simplified for now - just UI updates)
            return

        # Normal chat
        # Add user message to UI
        history_list.history.append({"type": "user", "text": user_message})
        history_list.query_one("#chat-history-scroll").mount(MessageBubble({"type": "user", "text": user_message}))
        
        # Add loading AI message
        self.current_ai_text = ""
        ai_message_data = {"type": "gemini", "text": "Thinking..."}
        self.current_ai_bubble = MessageBubble(ai_message_data)
        history_list.query_one("#chat-history-scroll").mount(self.current_ai_bubble)
        history_list.query_one("#chat-history-scroll").scroll_end(animate=False)
        
        # Append to agent state and start turn
        app = self.app
        app.session_state.add_message(Message(role=Role.USER, content=user_message))
        app.run_agent_turn()

    def handle_agent_event(self, event: AgentEvent) -> None:
        """Handle events from the AgentExecutor (runs on main thread)."""
        history_list = self.query_one(HistoryList)
        scroll = history_list.query_one("#chat-history-scroll")

        if event.type == AgentEventType.TEXT_CHUNK:
            chunk = event.data.get("chunk", "")
            self.current_ai_text += chunk
            if self.current_ai_bubble:
                self.current_ai_bubble.update_text(self.current_ai_text)
                scroll.scroll_end(animate=False)

        elif event.type == AgentEventType.TOOL_CALL:
            tool_name = event.data.get("tool_name", "unknown")
            text = f"🛠️  Running tool: `{tool_name}`..."
            
            if self.current_ai_bubble:
                # Append tool call info to current bubble or create a new one
                self.current_ai_text += f"\n\n{text}\n"
                self.current_ai_bubble.update_text(self.current_ai_text)
            else:
                self.current_ai_text = text
                self.current_ai_bubble = MessageBubble({"type": "system", "text": text})
                scroll.mount(self.current_ai_bubble)
                
            scroll.scroll_end(animate=False)

        elif event.type == AgentEventType.TOOL_RESULT:
            tool_name = event.data.get("tool_name", "unknown")
            error = event.data.get("error")
            
            if error:
                text = f"❌ Tool `{tool_name}` failed: {error}"
            else:
                text = f"✅ Tool `{tool_name}` completed."
                
            if self.current_ai_bubble:
                self.current_ai_text += f"{text}\n\n"
                self.current_ai_bubble.update_text(self.current_ai_text)
                
            scroll.scroll_end(animate=False)

        elif event.type == AgentEventType.TURN_COMPLETE:
            # Turn is done, clear current bubble ref
            self.current_ai_bubble = None
            self.current_ai_text = ""
            scroll.scroll_end(animate=False)

    def handle_error(self, err_msg: str) -> None:
        """Handle fatal errors from the agent loop."""
        history_list = self.query_one(HistoryList)
        scroll = history_list.query_one("#chat-history-scroll")
        
        err_bubble = MessageBubble({"type": "error", "text": f"⚠️ {err_msg}"})
        scroll.mount(err_bubble)
        scroll.scroll_end(animate=False)
        
        self.current_ai_bubble = None
        self.current_ai_text = ""
