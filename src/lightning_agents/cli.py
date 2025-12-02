#!/usr/bin/env python3
"""
Lightning Agents CLI

Dynamic agent instantiation using the Factory-of-Factories pattern.

Usage:
    lightning list                          List all available agents
    lightning run <agent> "<prompt>"        Run an agent with a prompt
    lightning architect "<task>"            Create a new agent (uses CRUD tools)
    lightning db list-agents                List agents in database
    lightning db list-tools                 List tools in database
    lightning db get-agent <id>             Get agent details
    lightning db get-tool <id>              Get tool details
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from .registry import AgentRegistry, get_default_db_path
from .agent_factory import AgentDefinition
from .runner import run_agent_by_id
from .tools.db_utils import get_agents_db_path, get_tools_db_path, read_json_db


def get_agents_path() -> Path:
    """Get path to db/agents.json (in project root db/ directory)."""
    return get_default_db_path()


def cmd_list(registry: AgentRegistry) -> None:
    """List all available agents."""
    print("\nAvailable agents:\n")

    for agent_id in registry.list_agents():
        defn = registry.get_definition(agent_id)
        model_badge = f"[{defn.model}]"
        tools_badge = f"tools: {len(defn.tools)}" if defn.tools else "no tools"

        print(f"  {agent_id}")
        print(f"    {defn.description}")
        print(f"    {model_badge} {tools_badge}")
        print()


async def cmd_run(registry: AgentRegistry, agent_id: str, prompt: str) -> None:
    """Run an agent with a prompt."""
    try:
        defn = registry.get_definition(agent_id)
    except KeyError:
        print(f"Error: Agent '{agent_id}' not found.")
        print(f"Available: {', '.join(registry.list_agents())}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Agent: {defn.name}")
    print(f"Model: {defn.model}")
    print(f"{'='*60}\n")

    await run_agent_by_id(registry, agent_id, prompt)


async def cmd_architect(registry: AgentRegistry, task: str) -> None:
    """Use architect agent to create a new agent definition.

    The architect now uses CRUD tools to persist agents directly.
    No JSON parsing needed - it calls db_create_agent internally.
    """
    print(f"\nArchitect creating agent for: {task}")
    print("-" * 60)

    # Run architect agent with streaming
    # It will use db_create_agent tool to persist the agent
    await run_agent_by_id(
        registry,
        "architect",
        f"Create an agent for: {task}",
        stream=True,
    )


def cmd_db_list_agents() -> None:
    """List all agents in the database."""
    db = read_json_db(get_agents_db_path())
    agents = db.get("agents", {})

    print(f"\nAgents in database ({len(agents)} total):\n")
    for agent_id, data in agents.items():
        model = data.get("model", "?")
        tools_count = len(data.get("tools", []))
        print(f"  {agent_id}")
        print(f"    {data.get('description', 'No description')}")
        print(f"    [{model}] tools: {tools_count}")
        print()


def cmd_db_list_tools() -> None:
    """List all tools in the database."""
    db = read_json_db(get_tools_db_path())
    tools = db.get("tools", {})

    print(f"\nTools in database ({len(tools)} total):\n")
    for tool_id, data in tools.items():
        mcp_server = data.get("mcp_server", "custom-tools")
        print(f"  {tool_id}")
        print(f"    {data.get('description', 'No description')}")
        print(f"    MCP: mcp__{mcp_server}__{tool_id}")
        print()


def cmd_db_get_agent(agent_id: str) -> None:
    """Get full details of an agent."""
    db = read_json_db(get_agents_db_path())
    agents = db.get("agents", {})

    if agent_id not in agents:
        print(f"Error: Agent '{agent_id}' not found.")
        print(f"Available: {', '.join(agents.keys())}")
        sys.exit(1)

    agent = agents[agent_id]
    print(f"\nAgent: {agent_id}")
    print("-" * 60)
    print(json.dumps(agent, indent=2))


def cmd_db_get_tool(tool_id: str) -> None:
    """Get full details of a tool."""
    db = read_json_db(get_tools_db_path())
    tools = db.get("tools", {})

    if tool_id not in tools:
        print(f"Error: Tool '{tool_id}' not found.")
        print(f"Available: {', '.join(tools.keys())}")
        sys.exit(1)

    tool = tools[tool_id]
    print(f"\nTool: {tool_id}")
    print("-" * 60)
    print(json.dumps(tool, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Lightning Agents - Dynamic agent instantiation demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lightning list
  lightning run basic_helper "What is the factory pattern?"
  lightning run aimug_researcher "What RAG tutorials does AIMUG have?"
  lightning architect "code reviewer for Python security issues"
  lightning db list-agents
  lightning db get-agent architect
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    subparsers.add_parser("list", help="List all available agents")

    # run command
    run_parser = subparsers.add_parser("run", help="Run an agent with a prompt")
    run_parser.add_argument("agent", help="Agent ID to run")
    run_parser.add_argument("prompt", help="Prompt to send to the agent")

    # architect command
    arch_parser = subparsers.add_parser(
        "architect", help="Create a new agent definition (uses CRUD tools)"
    )
    arch_parser.add_argument("task", help="Task description for the new agent")

    # db command with subcommands
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_subparsers = db_parser.add_subparsers(dest="db_command", required=True)

    # db list-agents
    db_subparsers.add_parser("list-agents", help="List all agents in database")

    # db list-tools
    db_subparsers.add_parser("list-tools", help="List all tools in database")

    # db get-agent
    db_get_agent = db_subparsers.add_parser("get-agent", help="Get agent details")
    db_get_agent.add_argument("agent_id", help="Agent ID to get")

    # db get-tool
    db_get_tool = db_subparsers.add_parser("get-tool", help="Get tool details")
    db_get_tool.add_argument("tool_id", help="Tool ID to get")

    args = parser.parse_args()

    # Handle db commands (don't need registry)
    if args.command == "db":
        if args.db_command == "list-agents":
            cmd_db_list_agents()
        elif args.db_command == "list-tools":
            cmd_db_list_tools()
        elif args.db_command == "get-agent":
            cmd_db_get_agent(args.agent_id)
        elif args.db_command == "get-tool":
            cmd_db_get_tool(args.tool_id)
        return

    # Load registry for other commands
    agents_path = get_agents_path()
    if not agents_path.exists():
        print(f"Error: agents.json not found at {agents_path}")
        sys.exit(1)

    registry = AgentRegistry.from_json(agents_path)

    # Dispatch
    if args.command == "list":
        cmd_list(registry)
    elif args.command == "run":
        asyncio.run(cmd_run(registry, args.agent, args.prompt))
    elif args.command == "architect":
        asyncio.run(cmd_architect(registry, args.task))


if __name__ == "__main__":
    main()
