"""
Non-interactive CLI runner.
Ref: gemini-cli/packages/cli/src/nonInteractiveCli.ts

Used when running in a pipe or non-tty mode.
Takes input from stdin, runs the agent, and outputs to stdout.
"""

import asyncio
import sys
from typing import Optional

from kitten_cli.agents.executor import AgentExecutor, AgentEvent, AgentEventType
from kitten_cli.config.manager import ConfigManager
from kitten_cli.core.state import SessionState
from kitten_cli.core.types import Message, Role


class NonInteractiveCli:
    """Runs the agent in a non-interactive mode (e.g., piped input)."""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or ConfigManager()
        self.state = SessionState()
        self.executor = AgentExecutor(self.state, self.config_manager)

    async def run(self, initial_prompt: str) -> int:
        """Run the agent with an initial prompt."""
        
        # Add user message
        user_msg = Message(role=Role.USER, content=initial_prompt)
        self.state.add_message(user_msg)
        
        # Print input
        print(f"User: {initial_prompt}", file=sys.stderr)
        print("---", file=sys.stderr)

        final_response = ""
        
        try:
            async for event in self.executor.run():
                if event.type == AgentEventType.TOOL_CALL:
                    print(f"[Tool Call] {event.data.get('tool_name')}", file=sys.stderr)
                
                elif event.type == AgentEventType.TOOL_RESULT:
                    print(f"[Tool Result] {event.data.get('tool_name')} completed.", file=sys.stderr)
                
                elif event.type == AgentEventType.CONFIRMATION_REQUEST:
                    # Non-interactive mode cannot wait for confirmation.
                    # We must rely on the policy engine. If we hit ASK_USER, we auto-reject.
                    # Wait, the executor handles this if we implement auto-reject, 
                    # but typically non-interactive should be YOLO or fail.
                    print("[Warning] Tool required confirmation in non-interactive mode. Rejecting.", file=sys.stderr)
                    # The executor yields CONFIRMATION_REQUEST. We need a way to pass back the response.
                    # Actually, we should probably set the mode to auto-reject if interactive is False.
                    event.data["response_callback"]("reject")
                
                elif event.type == AgentEventType.TURN_COMPLETE:
                    msg = event.data.get("message", "")
                    if msg:
                        final_response += msg
                        
                elif event.type == AgentEventType.ERROR:
                    print(f"[Error] {event.data.get('error')}", file=sys.stderr)
                    return 1

        except KeyboardInterrupt:
            print("\n[Interrupted]", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"\n[Fatal Error] {e}", file=sys.stderr)
            return 1

        # Output the final response to stdout
        print(final_response)
        return 0


def run_non_interactive() -> int:
    """Entry point for non-interactive execution."""
    # Read from stdin if piped
    if not sys.stdin.isatty():
        input_text = sys.stdin.read().strip()
    else:
        # Or from arguments
        if len(sys.argv) > 1:
            input_text = " ".join(sys.argv[1:])
        else:
            print("Error: No input provided.", file=sys.stderr)
            return 1

    if not input_text:
        return 0

    cli = NonInteractiveCli()
    return asyncio.run(cli.run(input_text))


if __name__ == "__main__":
    sys.exit(run_non_interactive())
