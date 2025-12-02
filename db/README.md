# Lightning Agents Database

This directory contains the "databases" for lightning-agents - JSON files that store agent definitions and tool registrations.

## Schema Overview

### agents.json

Agent definitions that the system can instantiate at runtime.

```json
{
  "metadata": {
    "version": "1.0.0",
    "schema": "lightning-agents/db/agents",
    "created_at": "ISO-8601 timestamp",
    "updated_at": "ISO-8601 timestamp"
  },
  "agents": {
    "<agent_id>": {
      "name": "Human Readable Name",
      "description": "One-line description",
      "system_prompt": "Full system prompt for the agent",
      "model": "haiku|sonnet",
      "tools": ["mcp__server__tool_name", ...],
      "created_at": "ISO-8601 timestamp",
      "updated_at": "ISO-8601 timestamp"
    }
  }
}
```

### tools.json

Tool registrations for the custom-tools MCP server.

```json
{
  "metadata": {
    "version": "1.0.0",
    "schema": "lightning-agents/db/tools",
    "created_at": "ISO-8601 timestamp",
    "updated_at": "ISO-8601 timestamp"
  },
  "tools": {
    "<tool_id>": {
      "name": "Human Readable Name",
      "description": "What this tool does",
      "module": "python.module.path",
      "function": "function_name",
      "parameters": {
        "<param_name>": {
          "type": "string|number|boolean|object|array",
          "description": "Parameter description",
          "required": true|false
        }
      },
      "mcp_server": "custom-tools",
      "created_at": "ISO-8601 timestamp",
      "updated_at": "ISO-8601 timestamp"
    }
  }
}
```

## Voyager-Inspired Architecture

This database structure is inspired by NVIDIA's Voyager paper, where agents build and store a "skill library" that grows organically based on actual needs.

In lightning-agents:
- **agents.json** = Voyager's skill library (agents are the "skills")
- **tools.json** = Tool registry (capabilities agents can use)
- **CRUD tools** = How agents self-modify the database

Agents like `architect` can:
1. List existing agents (`db_list_agents`)
2. Create new agents (`db_create_agent`)
3. Update agents (`db_update_agent`)
4. Delete agents (`db_delete_agent`)

This enables the system to evolve and grow based on real-world needs, just like Voyager's skill library.

## CRUD Operations

Available via MCP tools (`mcp__custom-tools__db_*`):

### Agents
- `db_list_agents` - List all registered agents
- `db_get_agent` - Get agent by ID
- `db_create_agent` - Create new agent
- `db_update_agent` - Update existing agent
- `db_delete_agent` - Delete agent

### Tools
- `db_list_tools` - List all registered tools
- `db_get_tool` - Get tool by ID
- `db_create_tool` - Register new tool
- `db_update_tool` - Update existing tool
- `db_delete_tool` - Delete tool
