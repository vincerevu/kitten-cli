from pydantic import BaseModel, Field
from typing import Optional

class LLMConfig(BaseModel):
    """Configuration for a specific Language Model profile."""
    model: str = Field(default="gemini/gemini-1.5-pro")
    api_key: Optional[str] = Field(default=None)
    base_url: Optional[str] = Field(default=None)
    temperature: float = Field(default=0.0)
    top_p: float = Field(default=1.0)
    max_output_tokens: Optional[int] = Field(default=4096)

class AppConfig(BaseModel):
    """Global application configuration combining LLM and Agent settings."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    workspace_base: str = Field(default="./")
    max_iterations: int = Field(default=10)
    theme: str = Field(default="gemini-dark")
