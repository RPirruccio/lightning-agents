"""
Agent Runner - Execute agents with prompts.

Bridges AgentInstance → ClaudeSDKClient execution with MCP wiring.
"""

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
)

from .registry import AgentRegistry
from .agent_factory import AgentInstance
from .mcp_config import get_mcp_servers


async def run_agent(
    instance: AgentInstance,
    prompt: str,
    stream: bool = True,
) -> str:
    """
    Run an agent instance with a prompt.

    Args:
        instance: Configured AgentInstance from registry
        prompt: User prompt to send
        stream: Whether to stream output (default True)

    Returns:
        Complete response text
    """
    # Get MCP servers for this agent's tools
    mcp_servers = get_mcp_servers(instance.definition.tools)

    options = ClaudeAgentOptions(
        system_prompt=instance.prompt,
        allowed_tools=instance.definition.tools or [],
        mcp_servers=mcp_servers if mcp_servers else None,
    )

    response_text = ""

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        if stream:
                            print(block.text, end="", flush=True)
                        response_text += block.text

    if stream:
        print()  # Final newline

    return response_text


async def run_agent_by_id(
    registry: AgentRegistry,
    agent_id: str,
    prompt: str,
    runtime_opts: dict | None = None,
    stream: bool = True,
) -> str:
    """
    Convenience function: create instance from registry and run.

    Args:
        registry: AgentRegistry with loaded definitions
        agent_id: ID of agent to run
        prompt: User prompt
        runtime_opts: Optional runtime context to inject
        stream: Whether to stream output

    Returns:
        Complete response text
    """
    instance = registry.create(agent_id, runtime_opts)
    return await run_agent(instance, prompt, stream)
