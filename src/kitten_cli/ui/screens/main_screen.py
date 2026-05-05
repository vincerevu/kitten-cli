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
from kitten_cli.llm.client import KittenLLM

class MainScreen(Screen):
    """The main screen layout containing Header, Content, Inputs, and Footer."""

    def compose(self) -> ComposeResult:
        yield AppHeader()
        yield MainContent()
        yield Suggestions()
        yield ChatInput()
        yield AppFooter()
        
    def on_chat_input_submitted(self, event: ChatInput.Submitted) -> None:
        user_message = event.text
        history_list = self.query_one(HistoryList)
        
        # Add user message
        history_list.history.append({"type": "user", "text": user_message})
        history_list.query_one("#chat-history-scroll").mount(MessageBubble({"type": "user", "text": user_message}))
        
        # Add loading AI message
        ai_message_data = {"type": "gemini", "text": "..."}
        history_list.history.append(ai_message_data)
        ai_bubble = MessageBubble(ai_message_data)
        history_list.query_one("#chat-history-scroll").mount(ai_bubble)
        history_list.query_one("#chat-history-scroll").scroll_end(animate=False)
        
        # Trigger LLM
        self.stream_llm_response(user_message, ai_bubble)

    @work(exclusive=True)
    async def stream_llm_response(self, user_message: str, target_bubble: MessageBubble) -> None:
        client = KittenLLM()
        messages = [{"role": "user", "content": user_message}]
        
        full_response = ""
        target_bubble.update_text("") # Clear the loading dots
        
        async for chunk in client.stream_chat(messages):
            full_response += chunk
            target_bubble.update_text(full_response)
            
        # Update history store
        target_bubble.message_data["text"] = full_response
        
        # Ensure scroll is at the bottom when done
        history_list = self.query_one(HistoryList)
        history_list.query_one("#chat-history-scroll").scroll_end(animate=False)

