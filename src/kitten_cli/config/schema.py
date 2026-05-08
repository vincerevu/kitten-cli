"""
Config schema validation — Pydantic validators for config fields.
Ref: gemini-cli/packages/core/src/config/config.ts (zod schemas)
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class PolicyRule(BaseModel):
    """A single policy rule for tool approval."""
    tool: str = "*"
    action: str = "ask"  # "allow" | "deny" | "ask"
    glob: Optional[str] = None  # file glob pattern
    command: Optional[str] = None  # command prefix

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("allow", "deny", "ask"):
            raise ValueError(f"Invalid action '{v}', must be allow/deny/ask")
        return v


class ProjectConfig(BaseModel):
    """Per-project .kitten.toml configuration."""
    allowed_tools: List[str] = Field(default_factory=list)
    denied_tools: List[str] = Field(default_factory=list)
    policy_rules: List[PolicyRule] = Field(default_factory=list)
    system_prompt_append: str = ""
    sandbox_enabled: bool = False
    max_turns: Optional[int] = None
    max_time_minutes: Optional[int] = None


class McpServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    name: str
    command: str
    args: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    enabled: bool = True


class SettingsSchema(BaseModel):
    """
    Full settings schema — validates the merged config from
    global (~/.kitten/settings.json) + local (.kitten.toml).
    """
    model: str = "gemini/gemini-2.5-flash"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_output_tokens: int = 8192
    theme: str = "gemini-dark"
    sandbox: bool = False
    max_turns: int = 30
    max_time_minutes: int = 10
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    mcp_servers: List[McpServerConfig] = Field(default_factory=list)

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError(f"temperature must be between 0.0 and 2.0, got {v}")
        return v

    @field_validator("max_turns")
    @classmethod
    def validate_max_turns(cls, v: int) -> int:
        if v < 1:
            raise ValueError(f"max_turns must be >= 1, got {v}")
        return v
