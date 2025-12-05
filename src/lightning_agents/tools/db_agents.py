"""
Agent CRUD tools - MCP tools for managing .claude/agents/<id>/AGENT.md files.

These tools enable agents (like architect) to directly persist
new agent definitions to the filesystem.
"""

import json as json_module
import shutil

from claude_agent_sdk import tool

from .db_utils import (
    get_agents_base_path,
    get_timestamp,
    validate_agent_definition,
)
from ..agent_parser import parse_agent_md
from ..agent_writer import write_agent_md


def _list_agent_ids() -> list[str]:
    """Get list of all agent IDs from filesystem."""
    base = get_agents_base_path()
    if not base.exists():
        return []
    return sorted([
        d.name for d in base.iterdir()
        if d.is_dir() and (d / "AGENT.md").exists()
    ])


def _load_agent(agent_id: str) -> dict | None:
    """Load agent data from AGENT.md file."""
    base = get_agents_base_path()
    agent_file = base / agent_id / "AGENT.md"
    if not agent_file.exists():
        return None
    return parse_agent_md(agent_file)


@tool("db_list_agents", "List all registered agents", {})
async def db_list_agents(_args: dict) -> dict:
    """List all agents with their basic info."""
    base = get_agents_base_path()
    result = []

    for agent_id in _list_agent_ids():
        data = _load_agent(agent_id)
        if data:
            result.append({
                "id": agent_id,
                "name": data.get("name"),
                "description": data.get("description"),
                "model": data.get("model"),
                "tools_count": len(data.get("tools", [])),
            })

    return {
        "content": [{
            "type": "text",
            "text": f"Found {len(result)} agents:\n" + "\n".join(
                f"- {a['id']}: {a['description']} [{a['model']}]"
                for a in result
            )
        }]
    }


@tool("db_get_agent", "Get full details of an agent by ID", {"agent_id": str})
async def db_get_agent(args: dict) -> dict:
    """Get complete agent definition."""
    agent_id = args["agent_id"]
    data = _load_agent(agent_id)

    if not data:
        available = _list_agent_ids()
        return {
            "content": [{
                "type": "text",
                "text": f"Agent '{agent_id}' not found. Available: {', '.join(available)}"
            }],
            "isError": True
        }

    return {
        "content": [{
            "type": "text",
            "text": f"Agent: {agent_id}\n{json_module.dumps(data, indent=2)}"
        }]
    }


@tool(
    "db_create_agent",
    "Create a new agent definition",
    {
        "agent_id": str,
        "name": str,
        "description": str,
        "system_prompt": str,
        "model": str,
        "tools": list,
    }
)
async def db_create_agent(args: dict) -> dict:
    """Create a new agent definition as AGENT.md file."""
    agent_id = args["agent_id"]

    # Parse tools - SDK sends list as JSON string due to MCP schema bug
    tools = args.get("tools", [])
    if isinstance(tools, str):
        try:
            tools = json_module.loads(tools)
        except json_module.JSONDecodeError:
            tools = []

    # Parse skills if provided
    skills = args.get("skills", [])
    if isinstance(skills, str):
        try:
            skills = json_module.loads(skills)
        except json_module.JSONDecodeError:
            skills = []

    # Build agent data
    agent_data = {
        "name": args["name"],
        "description": args["description"],
        "system_prompt": args["system_prompt"],
        "model": args["model"],
        "tools": tools,
        "skills": skills,
        "subagents": args.get("subagents", []),
    }

    # Validate
    is_valid, error = validate_agent_definition(agent_data)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid agent definition: {error}"}],
            "isError": True
        }

    # Check if exists
    if _load_agent(agent_id):
        return {
            "content": [{"type": "text", "text": f"Agent '{agent_id}' already exists. Use db_update_agent to modify."}],
            "isError": True
        }

    # Add timestamps
    agent_data["created_at"] = get_timestamp()
    agent_data["updated_at"] = get_timestamp()

    # Write to filesystem
    base = get_agents_base_path()
    write_agent_md(agent_id, agent_data, base)

    return {
        "content": [{
            "type": "text",
            "text": f"Created agent '{agent_id}' successfully!\n\nName: {agent_data['name']}\nModel: {agent_data['model']}\nTools: {len(agent_data['tools'])}\n\nRun with: lightning run {agent_id} \"<prompt>\""
        }]
    }


@tool(
    "db_update_agent",
    "Update an existing agent definition",
    {
        "agent_id": str,
        "name": str,
        "description": str,
        "system_prompt": str,
        "model": str,
        "tools": list,
    }
)
async def db_update_agent(args: dict) -> dict:
    """Update an existing agent definition."""
    agent_id = args["agent_id"]

    # Load existing
    existing = _load_agent(agent_id)
    if not existing:
        return {
            "content": [{"type": "text", "text": f"Agent '{agent_id}' not found. Use db_create_agent to create."}],
            "isError": True
        }

    # Update only provided fields
    if "name" in args:
        existing["name"] = args["name"]
    if "description" in args:
        existing["description"] = args["description"]
    if "system_prompt" in args:
        existing["system_prompt"] = args["system_prompt"]
    if "model" in args:
        existing["model"] = args["model"]
    if "tools" in args:
        tools = args["tools"]
        if isinstance(tools, str):
            try:
                tools = json_module.loads(tools)
            except json_module.JSONDecodeError:
                tools = []
        existing["tools"] = tools
    if "skills" in args:
        skills = args["skills"]
        if isinstance(skills, str):
            try:
                skills = json_module.loads(skills)
            except json_module.JSONDecodeError:
                skills = []
        existing["skills"] = skills

    # Validate
    is_valid, error = validate_agent_definition(existing)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid agent definition: {error}"}],
            "isError": True
        }

    # Update timestamp
    existing["updated_at"] = get_timestamp()

    # Write to filesystem
    base = get_agents_base_path()
    write_agent_md(agent_id, existing, base)

    return {
        "content": [{
            "type": "text",
            "text": f"Updated agent '{agent_id}' successfully!"
        }]
    }


@tool("db_delete_agent", "Delete an agent definition", {"agent_id": str})
async def db_delete_agent(args: dict) -> dict:
    """Delete an agent's directory from filesystem."""
    agent_id = args["agent_id"]

    # Check exists
    data = _load_agent(agent_id)
    if not data:
        return {
            "content": [{"type": "text", "text": f"Agent '{agent_id}' not found."}],
            "isError": True
        }

    # Delete directory
    base = get_agents_base_path()
    agent_dir = base / agent_id
    if agent_dir.exists():
        shutil.rmtree(agent_dir)

    return {
        "content": [{
            "type": "text",
            "text": f"Deleted agent '{agent_id}' ({data['name']}) successfully!"
        }]
    }
