"""Custom tools for Lightning Agents - SDK MCP Server.

Includes:
- download_pdf: Download papers from URLs
- db_* tools: CRUD operations for agents and tools databases
- presentation tools: Generate and manage PPTX slides

NOTE: For basic file I/O, use SDK primitives (Read, Write, Edit, Bash)
      in the agent's tools list. Custom tools here are for domain-specific ops.
"""

from claude_agent_sdk import create_sdk_mcp_server

# Tool implementations
from .download_pdf import download_pdf
from .db_agents import (
    db_list_agents,
    db_get_agent,
    db_create_agent,
    db_update_agent,
    db_delete_agent,
)
from .db_tools import (
    db_list_tools,
    db_get_tool,
    db_create_tool,
    db_update_tool,
    db_delete_tool,
)
from .presentation import (
    generate_pptx,
    list_slides,
    add_slide,
    update_slide,
    delete_slide,
)

# Create an in-process SDK MCP server with all custom tools
custom_tools_server = create_sdk_mcp_server(
    name="custom-tools",
    version="0.4.0",
    tools=[
        # Download tools
        download_pdf,
        # Agent CRUD
        db_list_agents,
        db_get_agent,
        db_create_agent,
        db_update_agent,
        db_delete_agent,
        # Tool CRUD
        db_list_tools,
        db_get_tool,
        db_create_tool,
        db_update_tool,
        db_delete_tool,
        # Presentation tools
        generate_pptx,
        list_slides,
        add_slide,
        update_slide,
        delete_slide,
    ]
)

__all__ = [
    "custom_tools_server",
    "download_pdf",
    "db_list_agents",
    "db_get_agent",
    "db_create_agent",
    "db_update_agent",
    "db_delete_agent",
    "db_list_tools",
    "db_get_tool",
    "db_create_tool",
    "db_update_tool",
    "db_delete_tool",
    "generate_pptx",
    "list_slides",
    "add_slide",
    "update_slide",
    "delete_slide",
]
