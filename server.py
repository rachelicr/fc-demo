"""
server.py
~~~~~~~~~
Entry point. Wires together the MCP server with the tool definitions
and starts listening for connections from Claude Desktop.
"""

import asyncio

import mcp.server.stdio
from mcp.server import Server

from gmail_mcp.tools import TOOL_DEFINITIONS, handle_tool_call

server = Server("gmail-mcp-server")


@server.list_tools()
async def list_tools():
    return TOOL_DEFINITIONS


@server.call_tool()
async def call_tool(name, arguments):
    return await handle_tool_call(name, arguments)


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())