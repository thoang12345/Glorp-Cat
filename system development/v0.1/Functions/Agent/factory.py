from Functions.Model.config import CHATBOT_NAME
from Functions.Agent.agent import Agent
from Functions.Agent.conversations import Conversation
from Functions.Agent.toolManager import ToolManager
from Functions.MCP.manager import MCPManager
from Functions.Model.manager import ModelManager


SYSTEM_PROMPT = (
    f"You are {CHATBOT_NAME}. You are a helpful assistant. Have fun! :)"
    f"You have access to a vector database containing documents, handbooks, "
    f"notes, manuals, and other user-provided knowledge."
    f"When a question could reasonably be answered from these documents—even "
    f"if you have general knowledge about the topic—prefer retrieving the "
    f"relevant information first."
    f"If you do not know which collection is appropriate, call "
    f"`get_collections` before using `query_collection`."
    f"The 'handbook' database contains a 'arts_lab_graduate_handbook', that "
    f"contains information relating to graduate studies, conferences, paper "
    f"style guides and more."
)


class Runtime:
    def __init__(
        self,
        tool_manager,
        mcp_manager,
        model_manager
    ):
        self.tool_manager = tool_manager
        self.mcp_manager = mcp_manager
        self.model_manager = model_manager

    async def shutdown(self):
        await self.mcp_manager.shutdown()


async def create_runtime():
    tool_manager = ToolManager()
    mcp_manager = MCPManager()
    model_manager = ModelManager()

    await model_manager.load()

    await mcp_manager.add_server(
        "ddgs",
        command="ddgs",
        args=["mcp"]
    )

    await mcp_manager.add_server(
        "sequential_thinking",
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-sequential-thinking"
        ]
    )

    for tool in await mcp_manager.discover_tools():
        tool_manager.register(tool)

    return Runtime(
        tool_manager=tool_manager,
        mcp_manager=mcp_manager,
        model_manager=model_manager
    )


def create_agent(runtime, messages=None):
    conversation = Conversation(
        SYSTEM_PROMPT
    )

    if messages:
        for message in messages:
            if message["role"] == "user":
                conversation.add_user(
                    message["content"]
                )

            elif message["role"] == "assistant":
                conversation.add_assistant(
                    message.get("thinking") or "",
                    message["content"],
                    []
                )

    return Agent(
        tool_manager=runtime.tool_manager,
        conversation=conversation,
        mcp_manager=runtime.mcp_manager,
        model_manager=runtime.model_manager
    )