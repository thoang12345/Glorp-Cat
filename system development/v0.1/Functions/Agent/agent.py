from Functions.model import modelName, chatBotName, stream, thinking
from Functions.Agent.streaming import streamResponse
from Functions.Agent.toolManager import ToolManager
from Functions.Agent.conversations import Conversation

class Agent:
    def __init__(
        self,
        tool_manager,
        conversation,
        mcp_manager
    ):
        self.tool_manager = tool_manager
        self.conversation = conversation
        self.mcp_manager = mcp_manager

    async def chat(self, user_input):
        self.conversation.add_user(user_input)

        while True:
            assistant = await streamResponse(self.conversation.messages, self.tool_manager)

            self.conversation.add_assistant(
                assistant["thinking"],
                assistant["content"],
                assistant["tool_calls"]
            )

            if not assistant["tool_calls"]:
                break

            self.conversation.add_tool_messages(
                await self.tool_manager.execute_calls(
                    assistant["tool_calls"]
                )
            )

        return assistant["content"]