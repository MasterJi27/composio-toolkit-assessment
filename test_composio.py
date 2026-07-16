import os
from composio_langchain import ComposioToolSet, Action
from dotenv import load_dotenv

load_dotenv()
try:
    composio_toolset = ComposioToolSet(api_key=os.environ.get("COMPOSIO_API_KEY"))
    tools = composio_toolset.get_tools(actions=[Action.TAVILY_SEARCH_SEARCH])
    print("Tools retrieved:", tools)
except Exception as e:
    print(f"Error: {e}")
