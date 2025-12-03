"""
Tool CRUD tools - MCP tools for managing db/tools.json.

These tools enable agents (like tool_architect) to register
new custom tools in the database.
"""

from claude_agent_sdk import tool

from .db_utils import (
    get_tools_db_path,
    read_json_db,
    write_json_db,
    get_timestamp,
    validate_tool_definition,
)


@tool("db_list_tools", "List all registered tools in the database", {})
async def db_list_tools(args: dict) -> dict:
    """List all tools with their basic info."""
    db = read_json_db(get_tools_db_path())
    tools = db.get("tools", {})

    result = []
    for tool_id, tool_data in tools.items():
        result.append({
            "id": tool_id,
            "name": tool_data.get("name"),
            "description": tool_data.get("description"),
            "mcp_server": tool_data.get("mcp_server", "custom-tools"),
        })

    return {
        "content": [{
            "type": "text",
            "text": f"Found {len(result)} tools:\n" + "\n".join(
                f"- {t['id']}: {t['description']} (mcp__{t['mcp_server']}__{t['id']})"
                for t in result
            )
        }]
    }


@tool("db_get_tool", "Get full details of a tool by ID", {"tool_id": str})
async def db_get_tool(args: dict) -> dict:
    """Get complete tool definition."""
    tool_id = args["tool_id"]
    db = read_json_db(get_tools_db_path())
    tools = db.get("tools", {})

    if tool_id not in tools:
        return {
            "content": [{
                "type": "text",
                "text": f"Tool '{tool_id}' not found. Available: {', '.join(tools.keys())}"
            }],
            "isError": True
        }

    tool_data = tools[tool_id]
    import json
    return {
        "content": [{
            "type": "text",
            "text": f"Tool: {tool_id}\n{json.dumps(tool_data, indent=2)}"
        }]
    }


@tool(
    "db_create_tool",
    "Register a new tool in the database",
    {
        "tool_id": str,
        "name": str,
        "description": str,
        "module": str,
        "function": str,
        "parameters": dict,
        "mcp_server": str,
    }
)
async def db_create_tool(args: dict) -> dict:
    """Register a new tool definition."""
    import json as json_module

    tool_id = args["tool_id"]

    # Parse parameters - SDK sends dict as JSON string due to MCP schema bug
    parameters = args.get("parameters", {})
    if isinstance(parameters, str):
        try:
            parameters = json_module.loads(parameters)
        except json_module.JSONDecodeError:
            parameters = {}

    # Build tool data from args
    tool_data = {
        "name": args["name"],
        "description": args["description"],
        "module": args["module"],
        "function": args["function"],
        "parameters": parameters,
        "mcp_server": args.get("mcp_server", "custom-tools"),
    }

    # Validate
    is_valid, error = validate_tool_definition(tool_data)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid tool definition: {error}"}],
            "isError": True
        }

    # Read current DB
    db_path = get_tools_db_path()
    db = read_json_db(db_path)
    tools = db.get("tools", {})

    # Check if exists
    if tool_id in tools:
        return {
            "content": [{"type": "text", "text": f"Tool '{tool_id}' already exists. Use db_update_tool to modify."}],
            "isError": True
        }

    # Add timestamps and save
    tool_data["created_at"] = get_timestamp()
    tool_data["updated_at"] = get_timestamp()
    tools[tool_id] = tool_data
    db["tools"] = tools

    write_json_db(db_path, db)

    mcp_name = f"mcp__{tool_data['mcp_server']}__{tool_id}"

    return {
        "content": [{
            "type": "text",
            "text": f"Registered tool '{tool_id}' successfully!\n\nName: {tool_data['name']}\nMCP Name: {mcp_name}\nModule: {tool_data['module']}.{tool_data['function']}\n\nNote: The actual Python function must exist at the specified module path."
        }]
    }


@tool(
    "db_update_tool",
    "Update an existing tool in the database",
    {
        "tool_id": str,
        "name": str,
        "description": str,
        "module": str,
        "function": str,
        "parameters": dict,
        "mcp_server": str,
    }
)
async def db_update_tool(args: dict) -> dict:
    """Update an existing tool definition."""
    import json as json_module

    tool_id = args["tool_id"]

    # Read current DB
    db_path = get_tools_db_path()
    db = read_json_db(db_path)
    tools = db.get("tools", {})

    # Check exists
    if tool_id not in tools:
        return {
            "content": [{"type": "text", "text": f"Tool '{tool_id}' not found. Use db_create_tool to register."}],
            "isError": True
        }

    # Get existing and update
    existing = tools[tool_id]

    # Update only provided fields
    if "name" in args:
        existing["name"] = args["name"]
    if "description" in args:
        existing["description"] = args["description"]
    if "module" in args:
        existing["module"] = args["module"]
    if "function" in args:
        existing["function"] = args["function"]
    if "parameters" in args:
        # Parse parameters - SDK sends dict as JSON string due to MCP schema bug
        parameters = args["parameters"]
        if isinstance(parameters, str):
            try:
                parameters = json_module.loads(parameters)
            except json_module.JSONDecodeError:
                parameters = {}
        existing["parameters"] = parameters
    if "mcp_server" in args:
        existing["mcp_server"] = args["mcp_server"]

    # Validate
    is_valid, error = validate_tool_definition(existing)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid tool definition: {error}"}],
            "isError": True
        }

    # Update timestamp and save
    existing["updated_at"] = get_timestamp()
    tools[tool_id] = existing
    db["tools"] = tools

    write_json_db(db_path, db)

    return {
        "content": [{
            "type": "text",
            "text": f"Updated tool '{tool_id}' successfully!"
        }]
    }


@tool("db_delete_tool", "Delete a tool from the database", {"tool_id": str})
async def db_delete_tool(args: dict) -> dict:
    """Delete a tool registration."""
    tool_id = args["tool_id"]

    # Read current DB
    db_path = get_tools_db_path()
    db = read_json_db(db_path)
    tools = db.get("tools", {})

    # Check exists
    if tool_id not in tools:
        return {
            "content": [{"type": "text", "text": f"Tool '{tool_id}' not found."}],
            "isError": True
        }

    # Delete and save
    deleted = tools.pop(tool_id)
    db["tools"] = tools

    write_json_db(db_path, db)

    return {
        "content": [{
            "type": "text",
            "text": f"Deleted tool '{tool_id}' ({deleted['name']}) successfully!"
        }]
    }
