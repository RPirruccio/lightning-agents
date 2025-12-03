"""
Run Agent tool - enables agents to invoke other agents as sub-agents.

This is the key to the Voyager-style pattern where agents can delegate
to specialized sub-agents for specific tasks.
"""

import asyncio
from pathlib import Path
from claude_agent_sdk import tool


@tool(
    "run_agent",
    "Run another agent as a sub-agent with a specific prompt. Returns the agent's response. Use 'label' to identify sub-agents (e.g., 'slide_3').",
    {
        "agent_id": str,
        "prompt": str,
        "label": str,
    }
)
async def run_agent(args: dict) -> dict:
    """
    Invoke another agent from the registry and return its response.

    This enables the sub-agent pattern where one agent (like tool_architect)
    can delegate implementation work to another agent (like tool_implementer).

    Args:
        agent_id: ID of the agent to run
        prompt: The prompt to send to the sub-agent
        label: Optional label to identify this sub-agent instance (e.g., "slide_3")
    """
    from ..registry import AgentRegistry
    from ..runner import run_agent_capture
    from .db_utils import get_agents_db_path

    agent_id = args["agent_id"]
    prompt = args["prompt"]
    label = args.get("label", None)

    # Load registry
    try:
        registry = AgentRegistry.from_json(get_agents_db_path())
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Failed to load agent registry: {e}"}],
            "isError": True
        }

    # Create agent instance
    try:
        instance = registry.create(agent_id, {})
    except KeyError:
        available = list(registry.definitions.keys())
        return {
            "content": [{
                "type": "text",
                "text": f"Agent '{agent_id}' not found. Available: {', '.join(available)}"
            }],
            "isError": True
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Failed to create agent instance: {e}"}],
            "isError": True
        }

    # Run the sub-agent and capture output
    try:
        result = await run_agent_capture(instance, prompt, label=label, verbose=True)
        return {
            "content": [{
                "type": "text",
                "text": f"Sub-agent '{agent_id}' ({label or 'unlabeled'}) completed:\n\n{result}"
            }]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Sub-agent execution failed: {e}"}],
            "isError": True
        }
