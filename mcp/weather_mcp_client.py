"""MCP client that bridges agents to the weather MCP server."""

import asyncio
import json
from pathlib import Path
import sys

import nest_asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


nest_asyncio.apply()


class MCPWeatherClient:
    def _server_path(self) -> Path:
        return Path(__file__).parent / "weather_mcp_server.py"

    async def call_async(self, city: str) -> dict:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(self._server_path())],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("get_weather", {"city": city})
                content = getattr(result, "content", None)
                if content and hasattr(content[0], "text"):
                    return json.loads(content[0].text)
                return {"error": "No result from MCP server"}

    def call(self, city: str) -> dict:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.call_async(city))
