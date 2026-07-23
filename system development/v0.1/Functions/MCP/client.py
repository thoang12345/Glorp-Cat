from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class MCPClient:
    def __init__(self, command, args):
        self.server = StdioServerParameters(
            command=command,
            args=args,
        )
        self.session = None
        self._stdio = None

    async def __aenter__(self):
        self._stdio = stdio_client(self.server)
        read, write = await self._stdio.__aenter__()
        self.session = ClientSession(read, write)

        await self.session.__aenter__()
        await self.session.initialize()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(
            exc_type,
            exc,
            tb
        )

        await self._stdio.__aexit__(
            exc_type,
            exc,
            tb
        )

    async def list_tools(self):
        if self.session is None:
            raise RuntimeError("MCPClient is not connected.")

        return await self.session.list_tools()
    
    async def call_tool(self, name, arguments):
        if self.session is None:
            raise RuntimeError(
                "MCPClient is not connected."
            )

        return await self.session.call_tool(
            name,
            arguments
        )