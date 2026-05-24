from enum import Enum
from typing import Dict, List
from kitten_cli.policy.semantic_permissions import Rule

class AgentType(str, Enum):
    EXPLORE = "explore"
    PLAN = "plan"
    BUILD = "build"

# Default rulesets for different agent modes
# Based on the concept that explore should not modify, plan modifies docs, and build can do anything
AGENT_BASE_RULES: Dict[AgentType, List[Rule]] = {
    AgentType.EXPLORE: [
        Rule(permission="*", pattern="*", action="ask"),
        Rule(permission="read", pattern="*", action="allow"),
        Rule(permission="edit", pattern="*", action="deny"),
        Rule(permission="bash", pattern="*", action="deny"),
    ],
    AgentType.PLAN: [
        Rule(permission="*", pattern="*", action="ask"),
        Rule(permission="read", pattern="*", action="allow"),
        Rule(permission="edit", pattern="*.md", action="allow"),
        Rule(permission="edit", pattern="*", action="deny"),
    ],
    AgentType.BUILD: [
        Rule(permission="*", pattern="*", action="ask"),
        Rule(permission="read", pattern="*", action="allow"),
        Rule(permission="edit", pattern="*", action="allow"),
        # Bash permissions should still be explicitly requested unless configured otherwise
        Rule(permission="bash", pattern="*", action="ask"),
    ]
}

def get_rules_for_agent(agent_type: AgentType) -> List[Rule]:
    """Returns the base permission ruleset for the given agent type."""
    return AGENT_BASE_RULES.get(agent_type, [])
