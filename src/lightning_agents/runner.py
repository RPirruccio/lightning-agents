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
from claude_agent_sdk.types import ToolUseBlock, ToolResultBlock, ResultMessage

from .registry import AgentRegistry
from .agent_factory import AgentInstance
from .mcp_config import get_mcp_servers
from .agent_logger import AgentLogger


async def run_agent(
    instance: AgentInstance,
    prompt: str,
    stream: bool = True,
    verbose: bool = True,
) -> str:
    """
    Run an agent instance with a prompt.

    Args:
        instance: Configured AgentInstance from registry
        prompt: User prompt to send
        stream: Whether to stream output (default True)
        verbose: Whether to log tool calls and results (default True)

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
    input_tokens = 0
    output_tokens = 0
    cost = 0.0

    # Use name for logging (convert to snake_case for filename)
    agent_name = instance.definition.name.lower().replace(" ", "_")
    with AgentLogger(agent_name) as logger:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            if stream:
                                logger.text(block.text)
                            response_text += block.text

                        elif isinstance(block, ToolUseBlock) and verbose:
                            tool_input = block.input if hasattr(block, "input") else None
                            logger.tool_use(block.name, tool_input)

                        elif isinstance(block, ToolResultBlock) and verbose:
                            content = str(block.content) if hasattr(block, "content") else None
                            is_error = getattr(block, "is_error", False)
                            logger.tool_result(content, is_error)

                elif isinstance(message, ResultMessage):
                    if hasattr(message, "usage") and message.usage:
                        usage = message.usage
                        if isinstance(usage, dict):
                            input_tokens = usage.get("input_tokens", 0)
                            output_tokens = usage.get("output_tokens", 0)
                        else:
                            input_tokens = getattr(usage, "input_tokens", 0)
                            output_tokens = getattr(usage, "output_tokens", 0)
                    if hasattr(message, "cost"):
                        cost = message.cost or 0.0

        if stream:
            logger.execution_complete(input_tokens, output_tokens, cost)

    return response_text


async def run_agent_capture(
    instance: AgentInstance,
    prompt: str,
    label: str | None = None,
    verbose: bool = True,
) -> str:
    """
    Run an agent and capture output (for sub-agent invocation).

    This is used by the run_agent tool to invoke sub-agents.
    When verbose=True, prints progress and writes to log file.

    Args:
        instance: Configured AgentInstance from registry
        prompt: User prompt to send
        label: Optional label for this sub-agent (e.g., "slide_3")
        verbose: Whether to print progress messages (default True)

    Returns:
        Complete response text
    """
    from pathlib import Path

    agent_id = instance.definition.name.lower().replace(" ", "_")
    sub_label = f"[sub:{label or agent_id}]"

    if verbose:
        print(f"\n    {sub_label} Starting...", flush=True)

    # Get MCP servers for this agent's tools
    mcp_servers = get_mcp_servers(instance.definition.tools)

    options = ClaudeAgentOptions(
        system_prompt=instance.prompt,
        allowed_tools=instance.definition.tools or [],
        mcp_servers=mcp_servers if mcp_servers else None,
    )

    response_text = ""
    tool_count = 0

    # Set up log file for sub-agent
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_name = f"{agent_id}_sub_{label or 'unnamed'}.log"
    log_file = log_dir / log_name

    with open(log_file, "w") as f:
        f.write(f"Sub-agent: {agent_id}\n")
        f.write(f"Label: {label}\n")
        f.write(f"Prompt: {prompt[:200]}...\n")
        f.write("=" * 60 + "\n\n")

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)

            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text
                            f.write(block.text)
                        elif isinstance(block, ToolUseBlock):
                            tool_count += 1
                            f.write(f"\n[Tool: {block.name}]\n")

        f.write(f"\n\n{'=' * 60}\n")
        f.write(f"Completed. Tools used: {tool_count}\n")

    if verbose:
        # Truncate response for display
        preview = response_text[:100].replace("\n", " ")
        if len(response_text) > 100:
            preview += "..."
        print(f"    {sub_label} Done ({tool_count} tools). Log: {log_file.name}", flush=True)

    return response_text


async def run_agent_by_id(
    registry: AgentRegistry,
    agent_id: str,
    prompt: str,
    runtime_opts: dict | None = None,
    stream: bool = True,
    verbose: bool = True,
) -> str:
    """
    Convenience function: create instance from registry and run.

    Args:
        registry: AgentRegistry with loaded definitions
        agent_id: ID of agent to run
        prompt: User prompt
        runtime_opts: Optional runtime context to inject
        stream: Whether to stream output
        verbose: Whether to log tool calls and results

    Returns:
        Complete response text
    """
    instance = registry.create(agent_id, runtime_opts)
    return await run_agent(instance, prompt, stream, verbose)
