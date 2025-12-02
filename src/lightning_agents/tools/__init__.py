"""Custom tools for Lightning Agents - SDK MCP Server."""

from claude_agent_sdk import create_sdk_mcp_server
from .download_pdf import download_pdf

# Create an in-process SDK MCP server with our custom tools
custom_tools_server = create_sdk_mcp_server(
    name="custom-tools",
    version="0.1.0",
    tools=[download_pdf]
)

__all__ = ["custom_tools_server", "download_pdf"]
