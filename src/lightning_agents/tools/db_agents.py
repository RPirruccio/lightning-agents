"""
Agent CRUD tools - MCP tools for managing db/agents.json.

These tools enable agents (like architect) to directly persist
new agent definitions to the database.
"""

from claude_agent_sdk import tool

from .db_utils import (
    get_agents_db_path,
    read_json_db,
    write_json_db,
    get_timestamp,
    validate_agent_definition,
)


@tool("db_list_agents", "List all registered agents in the database", {})
async def db_list_agents(args: dict) -> dict:
    """List all agents with their basic info."""
    db = read_json_db(get_agents_db_path())
    agents = db.get("agents", {})

    result = []
    for agent_id, agent_data in agents.items():
        result.append({
            "id": agent_id,
            "name": agent_data.get("name"),
            "description": agent_data.get("description"),
            "model": agent_data.get("model"),
            "tools_count": len(agent_data.get("tools", [])),
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
    db = read_json_db(get_agents_db_path())
    agents = db.get("agents", {})

    if agent_id not in agents:
        return {
            "content": [{
                "type": "text",
                "text": f"Agent '{agent_id}' not found. Available: {', '.join(agents.keys())}"
            }],
            "isError": True
        }

    agent = agents[agent_id]
    import json
    return {
        "content": [{
            "type": "text",
            "text": f"Agent: {agent_id}\n{json.dumps(agent, indent=2)}"
        }]
    }


@tool(
    "db_create_agent",
    "Create a new agent in the database",
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
    """Create a new agent definition."""
    agent_id = args["agent_id"]

    # Build agent data from args
    agent_data = {
        "name": args["name"],
        "description": args["description"],
        "system_prompt": args["system_prompt"],
        "model": args["model"],
        "tools": args.get("tools", []),
    }

    # Validate
    is_valid, error = validate_agent_definition(agent_data)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid agent definition: {error}"}],
            "isError": True
        }

    # Read current DB
    db_path = get_agents_db_path()
    db = read_json_db(db_path)
    agents = db.get("agents", {})

    # Check if exists
    if agent_id in agents:
        return {
            "content": [{"type": "text", "text": f"Agent '{agent_id}' already exists. Use db_update_agent to modify."}],
            "isError": True
        }

    # Add timestamps and save
    agent_data["created_at"] = get_timestamp()
    agent_data["updated_at"] = get_timestamp()
    agents[agent_id] = agent_data
    db["agents"] = agents

    write_json_db(db_path, db)

    return {
        "content": [{
            "type": "text",
            "text": f"Created agent '{agent_id}' successfully!\n\nName: {agent_data['name']}\nModel: {agent_data['model']}\nTools: {len(agent_data['tools'])}\n\nRun with: lightning run {agent_id} \"<prompt>\""
        }]
    }


@tool(
    "db_update_agent",
    "Update an existing agent in the database",
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

    # Read current DB
    db_path = get_agents_db_path()
    db = read_json_db(db_path)
    agents = db.get("agents", {})

    # Check exists
    if agent_id not in agents:
        return {
            "content": [{"type": "text", "text": f"Agent '{agent_id}' not found. Use db_create_agent to create."}],
            "isError": True
        }

    # Get existing and update
    existing = agents[agent_id]

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
        existing["tools"] = args["tools"]

    # Validate
    is_valid, error = validate_agent_definition(existing)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid agent definition: {error}"}],
            "isError": True
        }

    # Update timestamp and save
    existing["updated_at"] = get_timestamp()
    agents[agent_id] = existing
    db["agents"] = agents

    write_json_db(db_path, db)

    return {
        "content": [{
            "type": "text",
            "text": f"Updated agent '{agent_id}' successfully!"
        }]
    }


@tool("db_delete_agent", "Delete an agent from the database", {"agent_id": str})
async def db_delete_agent(args: dict) -> dict:
    """Delete an agent definition."""
    agent_id = args["agent_id"]

    # Read current DB
    db_path = get_agents_db_path()
    db = read_json_db(db_path)
    agents = db.get("agents", {})

    # Check exists
    if agent_id not in agents:
        return {
            "content": [{"type": "text", "text": f"Agent '{agent_id}' not found."}],
            "isError": True
        }

    # Delete and save
    deleted = agents.pop(agent_id)
    db["agents"] = agents

    write_json_db(db_path, db)

    return {
        "content": [{
            "type": "text",
            "text": f"Deleted agent '{agent_id}' ({deleted['name']}) successfully!"
        }]
    }
