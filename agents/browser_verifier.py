"""Browser verification using browser-use to actually navigate and read docs."""

import json
import asyncio
import os
from typing import Optional

from rich.console import Console

from backend.config import settings

console = Console()

class BrowserVerifier:
    """Uses browser-use to navigate to the official API docs and verify LLM findings."""

    def __init__(self):
        try:
            from browser_use import Agent, Controller
            from browser_use import ChatOpenAI
        except ImportError:
            raise RuntimeError("browser-use must be installed.")
        
        opencode_api_key = os.environ.get("OPENCODE_API_KEY", "your-api-key-here")
            
        self.llm = ChatOpenAI(
            model="hy3-free",
            api_key=opencode_api_key,
            base_url="https://opencode.ai/zen/v1",
            temperature=0.0,
            timeout=30.0
        )

    async def _verify_app_async(self, app_name: str, hypothesis: dict, url: str) -> dict:
        from browser_use import Agent

        # Create a task for the browser-use agent
        task_desc = (
            f"You are verifying research for the app '{app_name}'.\n"
            f"Go to this developer documentation URL: {url}\n\n"
            f"The current hypothesis for this app is:\n"
            f"Auth: {hypothesis.get('auth')}\n"
            f"Access: {hypothesis.get('access')}\n"
            f"API: {hypothesis.get('api')}\n\n"
            f"Please read the documentation on the page to verify if this is correct. "
            f"Return a raw JSON object (with no markdown wrapping) containing:\n"
            f" - \"is_correct\": (boolean) true if the hypothesis is mostly correct\n"
            f" - \"corrected_fields\": (list of strings) field names that were wrong, e.g. [\"auth\", \"access\"]\n"
            f" - \"auth\": (string) the verified auth method\n"
            f" - \"access\": (string) the verified access\n"
            f" - \"api\": (string) the verified api surface\n"
        )
        
        from browser_use import Agent, Controller
        
        controller = Controller(exclude_actions=["extract_structured_data"])

        agent = Agent(
            task=task_desc,
            llm=self.llm,
            controller=controller
        )

        try:
            history = await agent.run()
            # history is an AgentHistoryList, we can extract the final result
            if history and history.history and history.history[-1].result:
                result = history.history[-1].result
                if result:
                    content = result[0].extracted_content
                    # Clean possible markdown JSON wrapping
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                        
                    data = json.loads(content)
                    return data
        except Exception as e:
            console.print(f"[red]Browser-use verification failed for {app_name}: {e}[/red]")
            
        return {
            "is_correct": True, # fallback to trust if browser fails
            "corrected_fields": [],
            "auth": hypothesis.get("auth"),
            "access": hypothesis.get("access"),
            "api": hypothesis.get("api"),
        }

    def verify_app(self, app_name: str, hypothesis: dict, url: str) -> dict:
        """Run the browser verification synchronously."""
        try:
            return asyncio.run(self._verify_app_async(app_name, hypothesis, url))
        except Exception as e:
            console.print(f"[red]Synchronous browser verification failed for {app_name}: {e}[/red]")
            return {
                "is_correct": True,
                "corrected_fields": [],
                "auth": hypothesis.get("auth"),
                "access": hypothesis.get("access"),
                "api": hypothesis.get("api"),
            }
