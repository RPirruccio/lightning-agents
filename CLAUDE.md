# Claude Developer Notes

Developer-focused documentation for working with lightning-agents and the Claude Agent SDK.

---

## Environment Setup

### 1. Install with uv

```bash
cd lightning-agents
uv sync
```

This installs:
- `claude-agent-sdk` - Official Claude Agent SDK
- `pydantic` - Data validation
- `python-dotenv` - Environment management

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```
SEARXNG_URL=https://your-searxng-instance:8888
```

### 3. Verify Setup

```bash
lightning list
```

---

## CLI Usage

### List All Agents

```bash
lightning list
```

### Run Any Agent

```bash
lightning run <agent_id> "<prompt>"
```

Examples:
```bash
lightning run basic_helper "Explain the factory pattern"
lightning run aimug_researcher "What RAG tutorials does AIMUG have?"
lightning run lab_finder "Find LangGraph labs"
```

### Create New Agent (Architect)

```bash
lightning architect "<task description>"
```

The architect agent will:
1. Generate a JSON definition
2. Register it in the registry
3. Save it to `agents.json`
4. Make it immediately usable

---

## Code Architecture

### File Responsibilities

| File | Purpose |
|------|---------|
| `src/lightning_agents/cli.py` | CLI entry point (list/run/architect commands) |
| `src/lightning_agents/runner.py` | Agent execution with MCP wiring |
| `src/lightning_agents/registry.py` | Factory-of-Factories pattern |
| `src/lightning_agents/agent_factory.py` | AgentDefinition → AgentInstance |
| `src/lightning_agents/mcp_config.py` | MCP server configurations |
| `src/lightning_agents/agents.json` | Agent blueprints (6 agents) |

### Data Flow

```
CLI Command
    │
    ▼
registry.from_json("agents.json")
    │
    ▼
registry.create(agent_id, runtime_opts)
    │
    ▼
AgentInstance (definition + context)
    │
    ▼
runner.run_agent(instance, prompt)
    │
    ├── mcp_config.get_mcp_servers(tools)
    │
    ▼
ClaudeAgentOptions(
    system_prompt=instance.prompt,
    allowed_tools=instance.definition.tools,
    mcp_servers=mcp_servers
)
    │
    ▼
ClaudeSDKClient(options)
    │
    ▼
Response streamed to stdout
```

---

## MCP Integration

### How MCP Tools Work

1. Agent declares tools in `agents.json`:
   ```json
   "tools": ["mcp__searxng__searxng_web_search"]
   ```

2. `mcp_config.py` parses tool names and loads server configs:
   ```python
   def get_mcp_servers(tool_names: list[str]) -> dict:
       # "mcp__searxng__web_search" → needs "searxng" server
       needed = {t.split("__")[1] for t in tool_names if t.startswith("mcp__")}
       return {n: MCP_SERVERS[n] for n in needed}
   ```

3. `runner.py` passes servers to ClaudeAgentOptions:
   ```python
   options = ClaudeAgentOptions(
       mcp_servers=get_mcp_servers(instance.definition.tools),
       allowed_tools=instance.definition.tools,
   )
   ```

### Adding New MCP Servers

Edit `mcp_config.py`:

```python
NEW_SERVER = {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "mcp-new-server"],
    "env": {"CONFIG_VAR": os.getenv("CONFIG_VAR", "default")}
}

MCP_SERVERS = {
    "searxng": SEARXNG_SERVER,
    "new": NEW_SERVER,  # Add here
}
```

---

## Agent Definition Schema

```json
{
  "agent_id": {
    "name": "Human Readable Name",
    "description": "One-line description shown in `lightning list`",
    "system_prompt": "Full system prompt for the agent",
    "model": "haiku|sonnet",
    "tools": ["mcp__server__tool_name", ...]
  }
}
```

### Model Selection

- `haiku`: Fast, cheap. Use for simple tasks, formatting, classification.
- `sonnet`: Powerful reasoning. Use for complex analysis, code generation.

### Tool Naming Convention

```
mcp__<server_name>__<tool_name>
```

Examples:
- `mcp__searxng__searxng_web_search`
- `mcp__searxng__web_url_read`

---

## Extending the System

### Adding a New Agent (Manual)

1. Edit `src/lightning_agents/agents.json`:
   ```json
   "my_agent": {
     "name": "My Agent",
     "description": "Does something useful",
     "system_prompt": "You are...",
     "model": "sonnet",
     "tools": []
   }
   ```

2. Run it:
   ```bash
   lightning run my_agent "Test prompt"
   ```

### Adding a New Agent (Architect)

```bash
lightning architect "agent that reviews code for memory leaks"
```

The architect handles the JSON generation automatically.

### Creating Custom Tools

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("my_tool", "Does something", {"param": str})
async def my_tool(args):
    return {
        "content": [{"type": "text", "text": f"Result: {args['param']}"}]
    }

# Bundle into server
my_server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[my_tool]
)
```

Add to `mcp_config.py` and reference in agent definitions.

---

## Presentation Generation

### Setup

```bash
uv sync --extra presentation
```

### Generate Slides

```bash
uv run python -m presentation.generate_slides
# Output: presentation/output/lightning-agents.pptx
```

### Editing Content

Edit `presentation/slide_content.py`:
- `SLIDES` list defines all slides
- `DIAGRAMS` dict defines flow diagrams

Edit `presentation/styles.py`:
- `COLORS` for AIMUG branding (blue/orange)
- `FONTS` and `SIZES` for typography

---

## Troubleshooting

### "Agent not found"

```bash
lightning list  # Check available agents
```

### "MCP server failed"

Check `.env` has correct `SEARXNG_URL`.

### "Invalid JSON from architect"

The CLI handles markdown code block stripping. If it still fails, check the raw response in the error output.

### Import Errors

```bash
uv sync  # Reinstall dependencies
```

---

## Key Patterns

### 1. Runtime Context Injection

```python
# Good - inject at creation time
instance = registry.create("agent", {"user": "alice", "mode": "verbose"})

# Bad - mutating definitions
definition.system_prompt += extra_text
```

### 2. Architect Output Validation

```python
required = {"id", "name", "description", "system_prompt", "model", "tools"}
if not required.issubset(new_agent.keys()):
    raise ValueError("Invalid definition")
```

### 3. Registry Persistence

```python
registry.register(agent_id, definition)
registry.save_json("agents.json")  # Always persist!
```

---

## References

- [Claude Agent SDK Python](https://github.com/anthropics/claude-agent-sdk-python)
- [Anthropic API Docs](https://docs.anthropic.com)
- [Austin AI MUG](https://aimug.org)
- [SearXNG](https://docs.searxng.org)
