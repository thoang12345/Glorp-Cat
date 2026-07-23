class Conversation:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.reset()

    def add_user(self, content):

        self.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant(self, thinking, content, tool_calls):

        self.messages.append({
            "role": "assistant",
            "thinking": thinking,
            "content": content,
            "tool_calls": tool_calls
        })

    def add_tool(self, name, content):

        self.messages.append({
            "role": "tool",
            "name": name,
            "content": content
        })

    def add_tool_messages(self, tool_messages):
        self.messages.extend(tool_messages)

    def reset(self):
        self.messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

    def history(self):
        return self.messages