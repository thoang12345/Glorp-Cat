from Functions.MCP.client import MCPClient
from Functions.MCP.tool import DiscoveredMCPTool

class MCPServer:
    def __init__(self, command, args):

        self.client = MCPClient(
            command=command,
            args=args
        )

    async def connect(self):
        await self.client.__aenter__()

    async def disconnect(self):
        await self.client.__aexit__(
            None,
            None,
            None
        )

    async def discover_tools(self):
        discovered = []
        tools = await self.client.list_tools()

        for tool in tools.tools:
            discovered.append(
                DiscoveredMCPTool(
                    self.client,
                    tool
                )
            )

        return discovered