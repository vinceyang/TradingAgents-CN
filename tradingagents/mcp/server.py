"""
TradingAgents MCP Server
基于标准 MCP 协议的 stdio server
"""
import asyncio
import os
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import ListToolsResult, CallToolResult, TextContent

from .tools import get_tools, call_tool


# Server instance
app = Server("tradingagents-mcp")


@app.list_tools()
async def list_tools() -> ListToolsResult:
    """Handle list_tools request"""
    tools = get_tools()
    return ListToolsResult(tools=tools)


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle call_tool request"""
    try:
        result = await call_tool(name, arguments)
        return CallToolResult(content=result)
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f'{{"success": false, "error": {{"code": "EXECUTION_ERROR", "message": "{e}"}}}}'
            )],
            isError=True
        )


async def run():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Main entry point for CLI"""
    print("TradingAgents MCP Server", file=sys.stderr)
    print(f"Mode: {'online' if os.getenv('TRADINGAGENTS_ONLINE', 'true').lower() == 'true' else 'offline'}", file=sys.stderr)
    print("Use with Claude Code or OpenClaw MCP client", file=sys.stderr)
    asyncio.run(run())


if __name__ == "__main__":
    main()
