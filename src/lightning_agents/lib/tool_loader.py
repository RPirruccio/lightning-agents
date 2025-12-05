"""
Tool Loader - Dynamically loads tools from .claude/tools/ and creates MCP server.

Tools in .claude/tools/ are self-contained Python files with @tool decorated functions.
Framework tools (db_agents, db_skills, run_agent) are imported from lib/.
"""

import importlib.util
from pathlib import Path
from claude_agent_sdk import create_sdk_mcp_server

from .db_utils import get_project_root

# Framework tools (from lib/)
from .db_agents import (
    db_list_agents,
    db_get_agent,
    db_create_agent,
    db_update_agent,
    db_delete_agent,
)
from .db_skills import (
    db_list_skills,
    db_get_skill,
    db_create_skill,
)
from .run_agent import run_agent


def get_tools_path() -> Path:
    """Get the path to .claude/tools/ directory."""
    return get_project_root() / ".claude" / "tools"


def load_tools_from_claude() -> list:
    """
    Dynamically load all @tool decorated functions from .claude/tools/*.py

    Returns list of tool functions ready for MCP registration.
    """
    tools_dir = get_tools_path()
    loaded_tools = []

    if not tools_dir.exists():
        return loaded_tools

    for py_file in sorted(tools_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue

        try:
            # Dynamic import from file path
            spec = importlib.util.spec_from_file_location(
                py_file.stem,
                py_file
            )
            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find all @tool decorated functions
            # The SDK marks them with specific attributes
            for name in dir(module):
                if name.startswith("_"):
                    continue
                obj = getattr(module, name)
                # Check if it's a tool (has the tool metadata from SDK decorator)
                if callable(obj) and hasattr(obj, "__wrapped__"):
                    loaded_tools.append(obj)

        except Exception as e:
            print(f"Warning: Failed to load tool from {py_file}: {e}")
            continue

    return loaded_tools


def get_custom_tools_server():
    """
    Create the custom-tools MCP server with all tools.

    Combines:
    - Framework tools (db_agents, db_skills, run_agent) from lib/
    - Extensible tools from .claude/tools/
    """
    # Framework tools (always available)
    framework_tools = [
        # Agent CRUD
        db_list_agents,
        db_get_agent,
        db_create_agent,
        db_update_agent,
        db_delete_agent,
        # Skill CRUD
        db_list_skills,
        db_get_skill,
        db_create_skill,
        # Sub-agent invocation
        run_agent,
    ]

    # Load extensible tools from .claude/tools/
    claude_tools = load_tools_from_claude()

    # Combine all tools
    all_tools = framework_tools + claude_tools

    return create_sdk_mcp_server(
        name="custom-tools",
        version="1.0.0",
        tools=all_tools,
    )


# Create the server instance (lazy, on first import)
custom_tools_server = get_custom_tools_server()
