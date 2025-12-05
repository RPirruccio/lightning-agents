"""Hello World Tool - A simple test tool for verifying tool functionality."""

from claude_agent_sdk import tool


@tool("hello_world", "A simple test tool that returns 'Hello, World!' - useful for testing tool functionality.", {})
async def hello_world(args: dict) -> dict:
    """Return a 'Hello, World!' greeting.

    This is a simple test tool with no parameters that can be used
    to verify that the custom tools MCP server is working correctly.

    Returns:
        dict: MCP-style response containing the greeting message.
    """
    return {
        "content": [{
            "type": "text",
            "text": "Hello, World!"
        }]
    }
