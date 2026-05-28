# Kitten CLI 🐾

**Kitten CLI** is a powerful, terminal-based AI Coding Assistant, designed to help developers write code, brainstorm, and manage their workspaces. It features a beautiful, responsive Textual User Interface (TUI).

## 🌟 Features

- **Rich Terminal UI**: A gorgeous, hacker-friendly inline chat interface built with [Textual](https://textual.textualize.io/).
- **Inline Mode**: Blends seamlessly into your terminal flow without clearing your scrollback buffer.
- **AI-Powered**: Integrates with [LiteLLM](https://docs.litellm.ai/) for seamless connections to language models (defaulting to `gemini-2.5-flash`).
- **Context Aware**: Automatically picks up your current workspace directory and git branch.
- **Fast & Lightweight**: Built on Python 3.11+ using `Typer`, `Rich`, and modern async patterns.

## 🚀 Installation

Ensure you have Python 3.11 or higher installed. You can install Kitten CLI using `pip` or `uv`:

```bash
# Clone the repository
git clone https://github.com/vincerevu/kitten-cli.git
cd kitten-cli

# Install dependencies and the CLI tool
pip install -e .
```

If you are using `uv`:
```bash
uv pip install -e .
```

## 💻 Usage

To launch the interactive coding assistant, simply run:

```bash
kitten
```

This will launch the inline Textual interface where you can chat with the AI, ask questions about your codebase, and generate code.

### Commands

Kitten CLI is built on Typer. You can explore available commands by running:

```bash
kitten --help
```

## 🛠️ Configuration

Kitten CLI uses a robust configuration system (`pydantic-settings`). You can configure your environment using a `.env` file or a `.kitten.yaml` configuration file in your project root or home directory.

Example `.env`:
```env
GEMINI_API_KEY=your_api_key_here
```

## 🏗️ Architecture

- `src/kitten_cli/ui/` - Contains all Textual UI components (App, Header, Footer, ChatInput, HistoryList).
- `src/kitten_cli/cli/` - Typer command definitions and entry points.
- `src/kitten_cli/config/` - Settings, schemas, and workspace discovery logic.
- `src/kitten_cli/llm/` - LiteLLM wrappers and model definitions.
- `src/kitten_cli/services/` - Core services (Git, Memory, Shell Execution, Workspace analysis).

## 📄 License

This project is licensed under the MIT License.
