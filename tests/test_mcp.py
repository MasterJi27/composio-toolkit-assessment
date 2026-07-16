import asyncio
from composio import Composio
from composio_langchain import LangchainProvider
from backend.config import settings
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

async def main():
    c = Composio(provider=LangchainProvider(), api_key=settings.composio_api_key)
    session = c.create(user_id="test", toolkits=["exa"])
    mcp_url = session.mcp.url
    
    print("URL:", session.mcp.url)
    print("TYPE:", getattr(session.mcp, "type", None))
    print("HEADERS:", getattr(session.mcp, "headers", None))
    return
    
    try:
        async with client.session("composio-mcp") as mcp_session:
            tools = await load_mcp_tools(mcp_session)
            print("Successfully got tools:", tools)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Failed:", e)

if __name__ == "__main__":
    asyncio.run(main())
