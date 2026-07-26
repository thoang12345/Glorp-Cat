from Functions.Agent.streaming import streamResponse
from Functions.responseStats import ResponseStats

class Agent:
    def __init__(
        self,
        tool_manager,
        conversation,
        mcp_manager,
        model_manager
    ):
        self.tool_manager = tool_manager
        self.conversation = conversation
        self.mcp_manager = mcp_manager
        self.model_manager = model_manager

    async def chat(self, user_input):
        stats = ResponseStats()
        stats.set_model(
            self.model_manager.info
        )
        self.conversation.add_user(user_input)

        while True:
            assistant = await streamResponse(
                self.conversation.messages, 
                self.tool_manager,
                stats
                )

            self.conversation.add_assistant(
                assistant["thinking"],
                assistant["content"],
                assistant["tool_calls"]
            )

            if not assistant["tool_calls"]:
                break

            self.conversation.add_tool_messages(
                await self.tool_manager.execute_calls(
                    stats,
                    assistant["tool_calls"]
                )
            )

        stats.finish()
        stats.print_stats()

        return assistant["content"]