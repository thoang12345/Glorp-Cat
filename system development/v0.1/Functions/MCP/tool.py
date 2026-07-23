from Functions.tool import Tool

class DiscoveredMCPTool(Tool):

    def __init__(self, client, tool_info):
        super().__init__(
            tool_info.name,
            tool_info.description
        )

        self.client = client
        self.tool_info = tool_info

    def schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.tool_info.inputSchema
            }
        }

    async def execute(self, **kwargs):
        result = await self.client.call_tool(
            self.name,
            kwargs
        )

        return result.structuredContent