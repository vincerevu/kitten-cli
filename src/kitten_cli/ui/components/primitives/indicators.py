from textual.widget import Widget
from textual.widgets import LoadingIndicator
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.containers import Horizontal
from textual.widgets import Label

class CliSpinner(Widget):
    """A generic spinner wrapper mapped from CliSpinner.tsx"""
    
    DEFAULT_CSS = """
    CliSpinner {
        height: 1;
        width: auto;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield LoadingIndicator()


class ProgressBar(Widget):
    """An ASCII progress bar mapped from ProgressBar.tsx"""
    
    value = reactive(0)
    width = reactive(50)
    warning_threshold = reactive(80)
    
    DEFAULT_CSS = """
    ProgressBar {
        height: 1;
        width: auto;
    }
    .progress-active {
        color: $success;
    }
    .progress-warning {
        color: $warning;
    }
    .progress-error {
        color: $error;
    }
    .progress-inactive {
        color: $surface-light;
    }
    """
    
    def __init__(self, value: int = 0, width: int = 50, warning_threshold: int = 80, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.width = width
        self.warning_threshold = warning_threshold
        
    def render(self) -> str:
        safe_value = max(0, min(self.value, 100))
        active_chars = int((safe_value / 100) * self.width)
        inactive_chars = self.width - active_chars
        
        color_class = "progress-active"
        if safe_value >= 100:
            color_class = "progress-error"
        elif safe_value >= self.warning_threshold:
            color_class = "progress-warning"
            
        # Using rich markup for color
        active_str = "▬" * active_chars
        inactive_str = "▬" * inactive_chars
        
        return f"[{color_class}]{active_str}[/][progress-inactive]{inactive_str}[/]"
