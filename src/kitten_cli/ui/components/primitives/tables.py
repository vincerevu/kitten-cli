from textual.widget import Widget
from textual.widgets import DataTable
from textual.app import ComposeResult
from typing import List, Dict, Any

class Table(Widget):
    """Mapped from Table.tsx. Wraps Textual's DataTable."""
    
    DEFAULT_CSS = """
    Table {
        height: auto;
        min-height: 5;
    }
    """
    
    def __init__(self, data: List[Dict[str, Any]], columns: List[Dict[str, str]], **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.columns = columns
        self.table = DataTable()
        
    def compose(self) -> ComposeResult:
        yield self.table

    def on_mount(self) -> None:
        # Add columns
        for col in self.columns:
            self.table.add_column(col.get("header", col.get("key", "")))
            
        # Add rows
        for item in self.data:
            row = [str(item.get(col.get("key", ""), "")) for col in self.columns]
            self.table.add_row(*row)
