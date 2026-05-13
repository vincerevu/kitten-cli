"""
Types and constants for Context Management.
"""

# Number of tokens of tool outputs to protect from pruning
PRUNE_PROTECT = 40_000

# Minimum tokens to free to justify pruning
PRUNE_MINIMUM = 20_000

# Number of conversation turns at the end to keep intact during LLM compression
DEFAULT_TAIL_TURNS = 2

# Threshold (proportion of max tokens) before triggering LLM compression
COMPRESSION_THRESHOLD_RATIO = 0.8

# Structured Markdown template for session summaries
SUMMARY_TEMPLATE = """You are tasked with summarizing the conversation history up to this point.
Maintain all critical details, especially constraints, plans, and technical specifications.

Please format your response according to the following sections:

## Goal
[Briefly state the primary goal of the session]

## Constraints & Preferences
[List any explicit user constraints or preferences]

## Progress
### Done
- [Task 1]
- [Task 2]

### In Progress
- [Task 3]

### Blocked
- [Any blocked tasks]

## Key Decisions
- [Decision 1]

## Next Steps
- [Step 1]
- [Step 2]

## Critical Context
[Any important context that must not be forgotten, e.g., current architecture or state]

## Relevant Files
- [File 1]
- [File 2]
"""
