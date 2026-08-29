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

    async def chat(self, user_input, attachments=None, on_event=None):
        stats = ResponseStats()
        stats.set_model(
            self.model_manager.info
        )
        self.conversation.add_user(user_input, attachments)

        while True:
            assistant = await streamResponse(
                self.conversation.get_model_messages(),
                self.tool_manager,
                stats,
                on_event=on_event
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
                    assistant["tool_calls"],
                    on_event=on_event
                )
            )

        await self.model_manager.load_active()

        stats.finish()

        if on_event:
            await on_event({
                "type": "response_stats",
                "data": stats.to_dict()
            })

        stats.print_stats()

        return {
            "content": assistant["content"],
            "thinking": assistant["thinking"]
        }