from textual.widget import Widget
from textual.widgets import Markdown, Static
from textual.app import ComposeResult
from typing import Dict, Any

class MessageBubble(Widget):
    """A bubble displaying a single message in the history.
    Mapped from UserMessage.tsx, GeminiMessage.tsx, etc.
    """
    
    DEFAULT_CSS = """
    MessageBubble {
        width: 100%;
        height: auto;
        padding: 1 2;
        margin-bottom: 1;
        border: solid $surface-light;
    }
    
    .message-user {
        border-left: thick $accent;
        background: $surface;
    }
    
    .message-ai {
        border-left: thick $primary;
        background: $surface;
    }
    
    .message-system {
        border-left: thick $warning;
        color: $text-muted;
    }
    """
    
    def __init__(self, message: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.msg_type = message.get("type", "unknown")
        self.content = message.get("text", "")
        
    def compose(self) -> ComposeResult:
        # Assign CSS classes based on message type
        if self.msg_type in ["user", "user_shell"]:
            self.add_class("message-user")
        elif self.msg_type in ["gemini", "ai"]:
            self.add_class("message-ai")
        else:
            self.add_class("message-system")
            
        # For AI messages we might want to use Markdown rendering
        if self.msg_type in ["gemini", "ai"]:
            yield Markdown(self.content)
        else:
            prefix = "👤 " if self.msg_type in ["user", "user_shell"] else "⚙️ "
            yield Static(f"{prefix}{self.content}")
