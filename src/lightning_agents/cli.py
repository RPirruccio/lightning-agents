#!/usr/bin/env python3
"""
Lightning Agents CLI

Dynamic agent instantiation using the Factory-of-Factories pattern.
Agents are loaded from filesystem: .claude/agents/<id>/AGENT.md

Usage:
    lightning list                          List all available agents
    lightning run <agent> "<prompt>"        Run an agent with a prompt
    lightning architect "<task>"            Create a new agent (uses CRUD tools)
"""

import argparse
import asyncio
import os
import sys

# Force unbuffered output for real-time streaming
os.environ["PYTHONUNBUFFERED"] = "1"
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

from .lib import AgentRegistry, run_agent_by_id




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

    args = parser.parse_args()

    # Load registry from filesystem (.claude/agents/)
    registry = AgentRegistry.from_filesystem()

    # Dispatch
    if args.command == "list":
        cmd_list(registry)
    elif args.command == "run":
        asyncio.run(cmd_run(registry, args.agent, args.prompt))
    elif args.command == "architect":
        asyncio.run(cmd_architect(registry, args.task))


if __name__ == "__main__":
    main()
