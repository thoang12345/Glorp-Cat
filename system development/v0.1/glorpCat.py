import asyncio

from Functions.Model.config import CHATBOT_NAME
from Functions.system import giveGPUstatus
from Functions.Agent.agent import Agent
from Functions.Agent.conversations import Conversation
from Functions.Agent.toolManager import ToolManager
from Functions.MCP.manager import MCPManager
from Functions.Model.manager import ModelManager

giveGPUstatus()

async def main():
    tool_manager = ToolManager()
    mcp = MCPManager()
    model_manager = ModelManager()

    await model_manager.load()

    await mcp.add_server(
        "ddgs",
        command="ddgs",
        args=["mcp"]
    )

    await mcp.add_server(
        "sequential_thinking",
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-sequential-thinking"
        ]
    )

    for tool in await mcp.discover_tools():
        tool_manager.register(tool)

    for name in tool_manager.tools:
        print(f" - {name}")
        
    conversation = Conversation(
        f"You are {CHATBOT_NAME}. You are a helpful assistant. Have fun! :)"
        f"You have access to a vector database containing documents, handbooks, notes, manuals, and other user-provided knowledge."
        f"When a question could reasonably be answered from these documents—even if you have general knowledge about the topic—prefer retrieving the relevant information first."
        f"If you do not know which collection is appropriate, call `get_collections` before using `query_collection`."
        f"The 'Downey' database contains a 'arts_lab_graduate_handbook', that contains information relating to graduate studies, conferences, paper style guides and more."
    )

    agent = Agent(
        tool_manager=tool_manager,
        conversation=conversation,
        mcp_manager=mcp,
        model_manager=model_manager
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