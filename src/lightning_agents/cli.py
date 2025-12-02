#!/usr/bin/env python3
"""
Lightning Agents CLI

Dynamic agent instantiation using the Factory-of-Factories pattern.

Usage:
    lightning list                          List all available agents
    lightning run <agent> "<prompt>"        Run an agent with a prompt
    lightning architect "<task>"            Create a new agent definition
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from .registry import AgentRegistry
from .agent_factory import AgentDefinition
from .runner import run_agent_by_id


def get_agents_path() -> Path:
    """Get path to agents.json (same directory as this script)."""
    return Path(__file__).parent / "agents.json"


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
    """Use architect agent to create a new agent definition."""
    agents_path = get_agents_path()

    print(f"\nArchitect creating agent for: {task}")
    print("-" * 60)

    # Run architect agent (no streaming - need full JSON)
    response = await run_agent_by_id(
        registry,
        "architect",
        f"Create an agent for: {task}",
        stream=False,
    )

    # Parse JSON response
    try:
        text = response.strip()
        # Handle potential markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json) and last line (```)
            text = "\n".join(lines[1:-1])

        new_agent = json.loads(text.strip())
    except json.JSONDecodeError as e:
        print(f"\nError: Failed to parse architect response as JSON")
        print(f"Parse error: {e}")
        print(f"\nRaw response:\n{response}")
        sys.exit(1)

    # Validate required fields
    required = {"id", "name", "description", "system_prompt", "model", "tools"}
    missing = required - set(new_agent.keys())
    if missing:
        print(f"\nError: Missing required fields: {missing}")
        print(f"\nResponse was:\n{json.dumps(new_agent, indent=2)}")
        sys.exit(1)

    # Register and save
    agent_id = new_agent.pop("id")

    # Check if agent already exists
    if agent_id in registry.list_agents():
        print(f"\nWarning: Agent '{agent_id}' already exists. Overwriting.")

    definition = AgentDefinition.from_dict(new_agent)
    registry.register(agent_id, definition)
    registry.save_json(agents_path)

    print(f"\nCreated agent: {agent_id}")
    print(f"  Name: {definition.name}")
    print(f"  Model: {definition.model}")
    print(f"  Tools: {definition.tools or 'none'}")
    print(f"\nSaved to: {agents_path}")
    print(f"\nRun it with: lightning run {agent_id} \"<prompt>\"")


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
        "architect", help="Create a new agent definition"
    )
    arch_parser.add_argument("task", help="Task description for the new agent")

    args = parser.parse_args()

    # Load registry
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
