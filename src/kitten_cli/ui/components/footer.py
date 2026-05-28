from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from textual.containers import Grid

class AppFooter(Widget):
    """The application footer containing status and tips."""
    
    DEFAULT_CSS = """
    AppFooter {
        dock: bottom;
        height: 2;
        background: transparent;
        color: gray;
        border-top: solid #333333;
        padding-top: 0;
    }
    
    #footer-grid {
        grid-size: 5;
        grid-columns: 2fr 1fr 1fr 2fr 1fr;
    }
    
    .footer-col {
        height: 2;
    }
    
    .footer-title {
        color: gray;
    }
    
    .footer-value {
        color: white;
        text-style: bold;
    }
    
    .sandbox-value {
        color: #FF87AF;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        import os
        workspace = os.path.basename(os.getcwd())
        
        with Grid(id="footer-grid"):
            # Col 1: Workspace
            with Static(classes="footer-col"):
                yield Static("workspace (/directory)", classes="footer-title")
                yield Static(workspace, classes="footer-value")
                
            # Col 2: Branch
            with Static(classes="footer-col"):
                yield Static("branch", classes="footer-title")
                yield Static("main", classes="footer-value")
                
            # Col 3: Sandbox
            with Static(classes="footer-col"):
                yield Static("sandbox", classes="footer-title")
                yield Static("no sandbox", classes="sandbox-value")
                
            # Col 4: Model
            with Static(classes="footer-col"):
                yield Static("/model", classes="footer-title")
                yield Static("gemini-2.5-flash", classes="footer-value")
