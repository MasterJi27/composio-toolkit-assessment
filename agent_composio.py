import os
import json
import csv
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We will use Langchain and Composio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# You can also use composio_langchain tools when Composio API is configured
# from composio_langchain import ComposioToolSet, Action

def build_agent():
    """Builds the AI Agent that researches apps."""
    api_key = os.environ.get("OPENAI_API_KEY")
    kimchi_key = os.environ.get("KIMCHI_API_KEY")
    
    if kimchi_key and not api_key:
        print("Using KIMCHI API Serverless Model.")
        llm = ChatOpenAI(
            api_key=kimchi_key,
            base_url="https://llm.kimchi.dev/openai/v1",
            model="kimi-k2.7",
            temperature=0.1
        )
    elif api_key:
        llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0.1)
    else:
        raise ValueError("No LLM API Key found. Please set OPENAI_API_KEY or KIMCHI_API_KEY in .env")

    # In a full Composio setup, we would bind tools:
    # composio_toolset = ComposioToolSet(api_key=os.environ.get("COMPOSIO_API_KEY"))
    # tools = composio_toolset.get_tools(actions=[Action.TAVILY_SEARCH, Action.FIRECRAWL_SCRAPE])
    # llm_with_tools = llm.bind_tools(tools)
    
    # For now, we define the prompt and create the chain
    prompt = PromptTemplate.from_template(
        """You are an AI Product Ops Researcher.
Research the app: {app_name} (Website Hint: {hint}).

Output EXACTLY as a JSON object with the following structure, and nothing else:
{{
  "name": "{app_name}",
  "category": "Category name",
  "auth_type": "OAuth2, API key, Basic, token, or other",
  "access_status": "Self-serve or Gated",
  "api_surface": "REST/GraphQL breadth",
  "buildability": "Could this be an agent toolkit today? Any blocker?",
  "evidence_url": "URL to docs or evidence",
  "source_note": "Researched dynamically using LLM Agent pipeline"
}}
"""
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain

def research_app(chain, app_name: str, hint: str) -> Dict[str, Any]:
    try:
        response = chain.invoke({"app_name": app_name, "hint": hint})
        
        # Clean response if markdown block is present
        if response.startswith("```json"):
            response = response[7:-3]
        elif response.startswith("```"):
            response = response[3:-3]
            
        return json.loads(response.strip())
    except Exception as e:
        print(f"Error researching {app_name}: {e}")
        return {
            "name": app_name,
            "category": "Unknown",
            "auth_type": "Unknown",
            "access_status": "Unknown",
            "api_surface": "Unknown",
            "buildability": f"Error: {str(e)}",
            "evidence_url": hint,
            "source_note": "Fallback due to agent failure"
        }

if __name__ == "__main__":
    print("Initializing True Agentic Pipeline...")
    try:
        agent_chain = build_agent()
    except Exception as e:
        print(f"Initialization Failed: {e}")
        exit(1)

    # For demonstration, we'll run a small batch (e.g., 3 apps)
    test_apps = [
        {"name": "Salesforce", "hint": "salesforce.com"},
        {"name": "HubSpot", "hint": "hubspot.com"},
        {"name": "Notion", "hint": "developers.notion.com"},
    ]
    
    results = []
    print(f"Starting research on {len(test_apps)} apps...")
    for idx, app in enumerate(test_apps):
        print(f"[{idx+1}/{len(test_apps)}] Researching {app['name']}...")
        res = research_app(agent_chain, app['name'], app['hint'])
        results.append(res)
        time.sleep(2) # rate limit pause
        
    print("\nResearch Complete!")
    print(json.dumps(results, indent=2))
