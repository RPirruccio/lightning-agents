"""Custom tools for Lightning Agents - SDK MCP Server.

Includes:
- hello_world: Simple test tool for verifying functionality
- download_pdf: Download papers from URLs
- find_icon: Download icons from LobeHub's icon library
- db_* tools: CRUD operations for agents and tools databases
- presentation tools: Generate and manage PPTX slides
- run_agent: Sub-agent invocation tool (Voyager-style delegation)

NOTE: For basic file I/O, use SDK primitives (Read, Write, Edit, Bash)
      in the agent's tools list. Custom tools here are for domain-specific ops.
"""

from claude_agent_sdk import create_sdk_mcp_server

# Tool implementations
from .hello_world import hello_world
from .download_pdf import download_pdf
from .find_icon import find_icon
from .run_agent import run_agent
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
from .extract_slide_images import extract_slide_images

# Create an in-process SDK MCP server with all custom tools
custom_tools_server = create_sdk_mcp_server(
    name="custom-tools",
    version="0.5.0",
    tools=[
        # Test tools
        hello_world,
        # Download tools
        download_pdf,
        find_icon,
        # Sub-agent invocation (Voyager-style)
        run_agent,
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
        extract_slide_images,
    ]
)

__all__ = [
    "custom_tools_server",
    "hello_world",
    "download_pdf",
    "find_icon",
    "run_agent",
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
    "extract_slide_images",
]
