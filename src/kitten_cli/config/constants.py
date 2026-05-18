"""
Constants used across kitten-cli.
Ref: gemini-cli/packages/core/src/config/constants.ts
"""

# File names
KITTEN_CONFIG_FILE = ".kitten.toml"
KITTEN_IGNORE_FILE = ".kittenignore"
KITTEN_MEMORY_FILE = "KITTEN.md"
GLOBAL_SETTINGS_FILE = "settings.json"

# Agent defaults
DEFAULT_MAX_TURNS = 30
DEFAULT_MAX_TIME_MINUTES = 10
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OUTPUT_TOKENS = 8192

# Context window
DEFAULT_CONTEXT_WINDOW = 128_000
DEFAULT_COMPACTION_THRESHOLD = 0.7   # Compact when 70% full
DEFAULT_PRUNING_THRESHOLD = 40_000   # Start pruning at 40K tokens

# Tool execution
DEFAULT_TOOL_TIMEOUT = 120           # seconds
MAX_OUTPUT_BUFFER_SIZE = 16 * 1024 * 1024  # 16MB

# File discovery
MAX_DISCOVERY_FILES = 50_000
MAX_DISCOVERY_DEPTH = 20

# Loop detection
LOOP_MAX_IDENTICAL_CALLS = 3
LOOP_MAX_SIMILAR_OUTPUTS = 3
LOOP_WINDOW_SIZE = 10

# Model identifiers
DEFAULT_MODEL = "gemini/gemini-2.5-flash"
FALLBACK_MODEL = "gemini/gemini-2.5-flash"

# UI
SCROLLBACK_LIMIT = 300_000
