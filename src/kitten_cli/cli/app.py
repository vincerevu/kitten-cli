import typer
from kitten_cli.ui.app import KittenUI

app = typer.Typer(
    name="kitten",
    help="Kitten CLI - Your AI Coding Assistant",
    no_args_is_help=False,
    invoke_without_command=True
)

@app.callback()
def main():
    """Launch the Kitten CLI Textual Interface."""
    # When no command is specified, launch the UI
    ui = KittenUI()
    ui.run()

if __name__ == "__main__":
    app()
