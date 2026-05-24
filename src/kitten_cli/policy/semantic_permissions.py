from typing import List, Literal, Dict, Any, Set
import fnmatch
import os

Action = Literal["allow", "deny", "ask"]

class Rule:
    def __init__(self, permission: str, pattern: str, action: Action):
        self.permission = permission
        self.pattern = pattern
        self.action = action

    def __repr__(self) -> str:
        return f"Rule(permission='{self.permission}', pattern='{self.pattern}', action='{self.action}')"

EDIT_TOOLS = {"edit", "write", "apply_patch", "replace_file_content", "multi_replace_file_content", "write_to_file"}

def match_wildcard(pattern: str, string: str) -> bool:
    """Matches a string against a glob pattern. Handles simple * and ? like fnmatch."""
    # fnmatch matches full string if it doesn't contain *, so we use fnmatchcase.
    # In opencode, Wildcard.match simply does regex matching for * (converted to .*)
    return fnmatch.fnmatchcase(string, pattern)

def evaluate(permission: str, pattern: str, *rulesets: List[Rule]) -> Rule:
    """
    Evaluates a permission and pattern against a list of rulesets.
    The last matching rule in the flattened rulesets wins.
    If no rule matches, defaults to 'ask'.
    """
    flattened_rules = [rule for ruleset in rulesets for rule in ruleset]
    
    # Iterate in reverse (findLast)
    for rule in reversed(flattened_rules):
        if match_wildcard(rule.permission, permission) and match_wildcard(rule.pattern, pattern):
            return rule

    return Rule(permission=permission, pattern="*", action="ask")

def merge(*rulesets: List[Rule]) -> List[Rule]:
    """Merges multiple rulesets into one."""
    return [rule for ruleset in rulesets for rule in ruleset]

def disabled(tools: List[str], ruleset: List[Rule]) -> Set[str]:
    """
    Determines which tools are globally disabled by the ruleset.
    A tool is disabled if the last matching rule for its category with pattern '*' is 'deny'.
    """
    disabled_tools = set()
    for tool in tools:
        permission = "edit" if tool in EDIT_TOOLS else tool
        
        # Find last matching rule for this permission
        matching_rule = None
        for rule in reversed(ruleset):
            if match_wildcard(rule.permission, permission):
                matching_rule = rule
                break
                
        if matching_rule and matching_rule.pattern == "*" and matching_rule.action == "deny":
            disabled_tools.add(tool)
            
    return disabled_tools

def expand_pattern(pattern: str) -> str:
    """Expands ~ and $HOME in patterns."""
    if pattern.startswith("~/"):
        return os.path.expanduser("~") + pattern[1:]
    if pattern == "~":
        return os.path.expanduser("~")
    if pattern.startswith("$HOME/"):
        return os.path.expanduser("~") + pattern[5:]
    if pattern == "$HOME":
        return os.path.expanduser("~")
    return pattern

def from_config_dict(permission_config: Dict[str, Any]) -> List[Rule]:
    """
    Parses a config dictionary into a list of rules.
    Format:
    {
      "read": "allow",
      "edit": { "*.md": "allow", "*": "ask" }
    }
    """
    ruleset: List[Rule] = []
    for key, value in permission_config.items():
        if isinstance(value, str):
            ruleset.append(Rule(permission=key, pattern="*", action=value)) # type: ignore
        elif isinstance(value, dict):
            for pattern, action in value.items():
                expanded = expand_pattern(pattern)
                ruleset.append(Rule(permission=key, pattern=expanded, action=action)) # type: ignore
    return ruleset
