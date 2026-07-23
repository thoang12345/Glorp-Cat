import asyncio

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

server = StdioServerParameters(
    command="ddgs",
    args=["mcp"],
)

async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                "search_text",
                {
                    "query": "current Intel CEO",
                    "max_results": 5
                }
            )

            print(result)

if __name__ == "__main__":
    asyncio.run(main())