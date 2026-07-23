from Functions.model import modelName, chatBotName, stream, thinking
from Functions.Agent.streaming import streamResponse
from Functions.Agent.toolManager import ToolManager
from Functions.Agent.conversations import Conversation

class Agent:

    def __init__(self):

        self.tool_manager = ToolManager()
        self.conversation = Conversation(
            "You are a helpful assistant. :)"
        )

    def chat(self, user_input):
        self.conversation.add_user(user_input)
    
        while True:
            assistant = streamResponse(self.conversation.messages, self.tool_manager)

            self.conversation.add_assistant(
                    assistant["thinking"],
                    assistant["content"],
                    assistant["tool_calls"]
            )

            if not assistant["tool_calls"]:
                break

            self.conversation.add_tool_messages(
                self.tool_manager.execute_calls(
                    assistant["tool_calls"]
                )
            )

        return assistant["content"]