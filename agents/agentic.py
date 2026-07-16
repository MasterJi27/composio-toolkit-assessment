"""Real agentic researcher using Google Gemini and Composio MCP via Langchain."""

import json
import asyncio
import os
from typing import Optional

from rich.console import Console
from backend.config import settings

console = Console()

class AgenticResearcher:
    """Uses Google Gemini and Composio's MCP for actual web search via Langchain MCP adapters."""

    def __init__(self):
        try:
            from langchain_openai import ChatOpenAI
            from composio import Composio
            from composio_langchain import LangchainProvider
        except ImportError:
            raise RuntimeError("langchain-openai, composio, and langchain-mcp-adapters must be installed.")
        
        # Using OpenRouter free model as requested
        opencode_api_key = os.environ.get("OPENCODE_API_KEY", "your-api-key-here")
            
        self.llm = ChatOpenAI(
            model="hy3-free",
            openai_api_key=opencode_api_key,
            openai_api_base="https://opencode.ai/zen/v1",
            temperature=0.0,
            timeout=30.0
        )
        
        composio_api_key = settings.composio_api_key
        if not composio_api_key:
            raise ValueError("COMPOSIO_API_KEY is not set.")
            
        # Provision a Composio Session URL strictly for MCP use
        c = Composio(provider=LangchainProvider(), api_key=composio_api_key)
        session = c.create(user_id="researcher", toolkits=["exa"])
        self.mcp_url = session.mcp.url
        self.composio_api_key = composio_api_key
        
        # Cache tools to avoid 100 duplicate network calls
        self.use_tools = False
        self.tools = []
        try:
            from backend.composio_client import composio as _composio_cli
            _composio_cli._ensure_init()
            accounts = _composio_cli.get_connected_accounts()
            has_exa = any(a.get("app") == "exa" or a.get("appUniqueId") == "exa" for a in accounts) if accounts else False
            if has_exa:
                self.tools = c.tools.get(user_id="researcher", tools=["exa_search"])
                if self.tools:
                    self.use_tools = True
        except Exception:
            pass

    async def _research_app_async(self, app_name: str, hint_url: str) -> dict:
        from langchain_core.messages import HumanMessage, ToolMessage
        from langchain_mcp_adapters.client import MultiServerMCPClient

        prompt_text = (
            f"You are a Senior AI Product Ops Researcher.\n"
            f"Research the app '{app_name}' (Hint URL: {hint_url}). What auth does it use, what is the API surface, and is it gated?\n\n"
            "You must return ONLY a raw JSON object with exactly these keys:\n"
            ' - "auth": (string) e.g. "OAuth2", "API Key", "Basic"\n'
            ' - "access": (string) e.g. "Self-serve trial", "Enterprise gate", "Paid plan"\n'
            ' - "api": (string) e.g. "REST", "GraphQL", "CLI"\n'
            ' - "verdict": (string) e.g. "High potential: None" or "Low potential: Enterprise gate"\n'
            ' - "evidence": (string) The best developer URL you found.\n'
            "No markdown blocks, no other text."
        )

        messages = [HumanMessage(content=prompt_text)]
        
        response = None
        if self.use_tools:
            try:
                llm_with_tools = self.llm.bind_tools(self.tools)
                response = await llm_with_tools.ainvoke(messages)
                
                # Execute tools if requested
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    messages.append(response)
                    tool_map = {t.name: t for t in self.tools}
                    for tc in response.tool_calls:
                        tool = tool_map.get(tc["name"])
                        if tool:
                            result = await tool.ainvoke(tc["args"])
                            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
                    
                    response = await self.llm.ainvoke(messages)
            except Exception as e:
                response = await self.llm.ainvoke(messages)
        else:
            response = await self.llm.ainvoke(messages)

        content = response.content.strip()
        # Clean possible markdown JSON wrapping
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        data = json.loads(content)
        return {
            "auth": data.get("auth", "Unknown"),
            "access": data.get("access", "Unknown"),
            "api": data.get("api", "Unknown"),
            "verdict": data.get("verdict", "Unknown"),
            "evidence": data.get("evidence", hint_url),
            "mcp": "",
        }

    def research_app(self, app_name: str, hint_url: str) -> dict:
        """Use the LLM agent to find authentication and API details for a specific app."""
        try:
            return asyncio.run(self._research_app_async(app_name, hint_url))
        except Exception as e:
            import traceback
            traceback.print_exc()
            console.print(f"[red]Agentic research failed for {app_name}: {e}[/red]")
            return None
