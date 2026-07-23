import asyncio

from Functions.Agent.agent import Agent
from Functions.Agent.conversations import Conversation
from Functions.Agent.toolManager import ToolManager
from Functions.MCP.manager import MCPManager

async def main():
    tool_manager = ToolManager()
    

    mcp = MCPManager()

    await mcp.add_server(
        "ddgs",
        command="ddgs",
        args=["mcp"]
    )

    for tool in await mcp.discover_tools():
        tool_manager.register(tool)

    for name in tool_manager.tools:
        print(f" - {name}")
        
    conversation = Conversation(
        "You are GlorpCat. You are a helpful assistant. :)"
    )

    agent = Agent(
        tool_manager=tool_manager,
        conversation=conversation,
        mcp_manager=mcp
    )

    try:
        while True:
            user = input("\n\nYou: ")

            if not user:
                break
            await agent.chat(user)

    finally:
        await mcp.shutdown()

if __name__ == "__main__":
    asyncio.run(main())