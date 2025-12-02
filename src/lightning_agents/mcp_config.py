"""
MCP Server Configuration - External tool integrations.

Loads configuration from environment variables (.env file).
Provides MCP server configs that agents can use for tools.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SearXNG configuration
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8888")

# MCP Server definitions (external services)
SEARXNG_SERVER = {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "mcp-searxng"],
    "env": {"SEARXNG_URL": SEARXNG_URL},
}

# Registry of external MCP servers
MCP_SERVERS = {
    "searxng": SEARXNG_SERVER,
}


def get_mcp_servers(tool_names: list[str]) -> dict:
    """
    Get MCP server configs for the requested tools.

    Parses tool names in format "mcp__<server>__<tool>" and returns configs
    for the servers needed to provide those tools.

    For "custom-tools" server, returns the in-process SDK MCP server.

    Args:
        tool_names: List of tool names like ["mcp__searxng__searxng_web_search", "mcp__custom-tools__download_pdf"]

    Returns:
        Dict of server_name -> config for needed servers
    """
    from .tools import custom_tools_server

    result = {}
    needed_servers = set()

    for tool in tool_names:
        if tool.startswith("mcp__"):
            parts = tool.split("__")
            if len(parts) >= 2:
                needed_servers.add(parts[1])

    # Add servers
    for name in needed_servers:
        if name == "custom-tools":
            # In-process SDK MCP server
            result[name] = custom_tools_server
        elif name in MCP_SERVERS:
            # External MCP server
            result[name] = MCP_SERVERS[name]

    return result
