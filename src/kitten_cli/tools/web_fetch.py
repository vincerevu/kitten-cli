
import asyncio
from typing import Any, Optional
from kitten_cli.tools.base import DeclarativeTool, ToolKind, ToolResult


class WebFetchTool(DeclarativeTool):
    def __init__(self):
        super().__init__(
            name="web_fetch",
            display_name="Fetch URL",
            description="Fetch the content of a web page URL and return it as text/markdown.",
            kind=ToolKind.SEARCH,
            parameter_schema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch.",
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Max characters to return. Default 50000.",
                    },
                },
                "required": ["url"],
            },
        )

    async def execute(
        self,
        url: str,
        max_length: int = 50000,
        **kwargs: Any,
    ) -> ToolResult:
        try:
            import httpx
        except ImportError:
            return ToolResult(
                llm_content="Error: httpx not installed. Run: pip install httpx",
                error={"message": "httpx not installed"},
            )

        try:
            async with httpx.AsyncClient(
                follow_redirects=True, timeout=30.0
            ) as client:
                response = await client.get(url, headers={
                    "User-Agent": "KittenCLI/1.0 (compatible; bot)"
                })
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")

                if "text/html" in content_type:
                    text = self._html_to_text(response.text)
                else:
                    text = response.text

                if len(text) > max_length:
                    text = text[:max_length] + f"\n... [truncated, {len(text)} total chars]"

                return ToolResult(
                    llm_content=f"Content from {url}:\n\n{text}"
                )
        except httpx.HTTPStatusError as ex:
            return ToolResult(
                llm_content=f"Error: HTTP {ex.response.status_code} from {url}",
                error={"message": f"HTTP {ex.response.status_code}"},
            )
        except Exception as ex:
            return ToolResult(
                llm_content=f"Error fetching URL: {ex}",
                error={"message": str(ex)},
            )

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Simple HTML to text conversion."""
        import re
        # Remove script and style
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Convert br and p to newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</h[1-6]>', '\n\n', text, flags=re.IGNORECASE)
        # Strip remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode common entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ').replace('&quot;', '"')
        # Collapse whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
