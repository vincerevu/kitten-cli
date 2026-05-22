"""
Confirmation dialog for tool execution.
Ref: gemini-cli/packages/cli/src/ui/ToolConfirmationFullFrame.tsx

Presents the user with a tool call that requires approval.
Allows: Approve (once), Always Allow (add to policy), YOLO (change mode), Reject.
"""

import json
from typing import Any, Dict

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Label
from rich.syntax import Syntax
from rich.text import Text


class ConfirmationResult:
    """Result from the confirmation dialog."""
    def __init__(self, action: str):
        self.action = action  # "approve", "always", "yolo", "reject"


class ToolConfirmationDialog(ModalScreen[ConfirmationResult]):
    """Modal dialog to ask for tool execution confirmation."""

    DEFAULT_CSS = """
    ToolConfirmationDialog {
        align: center middle;
        background: $background 80%;
    }

    #dialog-container {
        width: 80%;
        height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #dialog-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        content-align: center middle;
    }

    #tool-details {
        height: 1fr;
        border: solid $surface-light;
        padding: 1;
        margin-bottom: 1;
        background: $boost;
    }

    #button-container {
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, tool_name: str, tool_args: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.tool_args = tool_args

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"⚠️ Tool Confirmation Required: [bold]{self.tool_name}[/bold]", id="dialog-title"),
            VerticalScroll(
                Static(self._format_args(), expand=True),
                id="tool-details"
            ),
            Horizontal(
                Button("Approve (Once)", variant="primary", id="btn-approve"),
                Button("Always Allow", variant="success", id="btn-always"),
                Button("YOLO Mode", variant="warning", id="btn-yolo"),
                Button("Reject", variant="error", id="btn-reject"),
                id="button-container"
            ),
            id="dialog-container"
        )

    def _format_args(self) -> Any:
        """Format the arguments for display."""
        try:
            # Check if it's a shell command for special formatting
            if self.tool_name == "run_command" and "command" in self.tool_args:
                code = self.tool_args["command"]
                return Syntax(code, "bash", theme="monokai", word_wrap=True)
            
            # Check if it's a file edit
            if self.tool_name == "edit_file" or self.tool_name == "write_file":
                path = self.tool_args.get("path", "unknown")
                content = self.tool_args.get("content", "")
                if self.tool_name == "edit_file":
                    content = self.tool_args.get("new_text", "")
                header = f"File: {path}\n\n"
                code_syntax = Syntax(content, "python", theme="monokai", word_wrap=True)
                return Vertical(Label(header), Static(code_syntax))
                
            # Default JSON dump
            formatted_json = json.dumps(self.tool_args, indent=2)
            return Syntax(formatted_json, "json", theme="monokai", word_wrap=True)
        except Exception as e:
            return Text(f"Error formatting args: {e}\n{self.tool_args}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "btn-approve":
            self.dismiss(ConfirmationResult("approve"))
        elif button_id == "btn-always":
            self.dismiss(ConfirmationResult("always"))
        elif button_id == "btn-yolo":
            self.dismiss(ConfirmationResult("yolo"))
        elif button_id == "btn-reject":
            self.dismiss(ConfirmationResult("reject"))
