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

The architect agent now uses **CRUD tools** to persist agents directly (Voyager-style):
1. Lists existing agents to avoid duplicates
2. Calls `db_create_agent` to persist the new agent
3. Agent is immediately usable

### Database Commands

```bash
lightning db list-agents           # List all agents in db/
lightning db list-tools            # List all tools in db/
lightning db get-agent <id>        # Get full agent definition
lightning db get-tool <id>         # Get full tool definition
```

---

## Code Architecture

### Directory Structure

```
lightning-agents/
├── db/                              # Database files (decoupled from code)
│   ├── agents.json                  # Agent definitions
│   ├── tools.json                   # Tool registry
│   └── README.md                    # Schema documentation
├── src/lightning_agents/
│   ├── tools/
│   │   ├── __init__.py              # SDK MCP server with all tools
│   │   ├── download_pdf.py          # PDF download tool
│   │   ├── db_utils.py              # Shared DB utilities
│   │   ├── db_agents.py             # Agent CRUD tools
│   │   └── db_tools.py              # Tool CRUD tools
│   ├── cli.py                       # CLI entry point
│   ├── runner.py                    # Agent execution
│   ├── registry.py                  # Factory-of-Factories pattern
│   ├── agent_factory.py             # AgentDefinition → AgentInstance
│   └── mcp_config.py                # MCP server configurations
```

### File Responsibilities

| File | Purpose |
|------|---------|
| `db/agents.json` | Agent definitions with metadata |
| `db/tools.json` | Tool registry with metadata |
| `src/lightning_agents/cli.py` | CLI entry point (list/run/architect/db commands) |
| `src/lightning_agents/runner.py` | Agent execution with MCP wiring |
| `src/lightning_agents/registry.py` | Factory-of-Factories pattern |
| `src/lightning_agents/tools/db_agents.py` | Agent CRUD tools (db_list_agents, db_create_agent, etc.) |
| `src/lightning_agents/tools/db_tools.py` | Tool CRUD tools (db_list_tools, db_create_tool, etc.) |

### Data Flow

```
CLI Command
    │
    ▼
registry.from_json("db/agents.json")
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
    │       │
    │       └── custom_tools_server (in-process)
    │               │
    │               └── db_* tools can modify db/agents.json
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

## Voyager-Inspired Architecture

Like NVIDIA's Voyager paper, lightning-agents uses a **self-modifying skill library**:

| Voyager | Lightning Agents |
|---------|------------------|
| Skill library (code) | `db/agents.json` (definitions) |
| Skills can compose | Agents can use tools |
| Add new skills | `db_create_agent` tool |
| Retrieve skills | `db_list_agents`, `db_get_agent` tools |

The `architect` agent can directly persist new agents by calling:
```
mcp__custom-tools__db_create_agent
```

This enables the system to **grow organically** based on actual needs.

---

## MCP Integration

### How MCP Tools Work

1. Agent declares tools in `db/agents.json`:
   ```json
   "tools": ["mcp__searxng__searxng_web_search", "mcp__custom-tools__db_list_agents"]
   ```

2. `mcp_config.py` parses tool names and loads server configs:
   ```python
   def get_mcp_servers(tool_names: list[str]) -> dict:
       # "mcp__custom-tools__db_list_agents" → needs "custom-tools" server
       # "mcp__searxng__web_search" → needs "searxng" server
   ```

3. Custom tools server is **in-process** (SDK MCP server):
   ```python
   custom_tools_server = create_sdk_mcp_server(
       name="custom-tools",
       tools=[download_pdf, db_list_agents, db_create_agent, ...]
   )
   ```

### Available Custom Tools

| Tool | Description |
|------|-------------|
| `mcp__custom-tools__download_pdf` | Download PDFs from URLs |
| `mcp__custom-tools__db_list_agents` | List all agents |
| `mcp__custom-tools__db_get_agent` | Get agent by ID |
| `mcp__custom-tools__db_create_agent` | Create new agent |
| `mcp__custom-tools__db_update_agent` | Update existing agent |
| `mcp__custom-tools__db_delete_agent` | Delete agent |
| `mcp__custom-tools__db_list_tools` | List all tools |
| `mcp__custom-tools__db_get_tool` | Get tool by ID |
| `mcp__custom-tools__db_create_tool` | Register new tool |
| `mcp__custom-tools__db_update_tool` | Update existing tool |
| `mcp__custom-tools__db_delete_tool` | Delete tool |
| `mcp__custom-tools__list_slides` | List presentation slides |
| `mcp__custom-tools__add_slide` | Add a slide at position |
| `mcp__custom-tools__update_slide` | Update slide by index |
| `mcp__custom-tools__delete_slide` | Delete slide by index |
| `mcp__custom-tools__generate_pptx` | Generate PowerPoint file |

---

## SDK Primitive Tools

The Claude Agent SDK provides built-in "primitive" tools that agents can use directly. These are NOT MCP tools - they're built into the SDK itself.

### Available Primitives

| Tool | Description |
|------|-------------|
| `Read` | Read file contents |
| `Write` | Write to files |
| `Edit` | Edit files interactively |
| `Bash` | Execute shell commands |
| `Grep` | Search file contents |
| `Glob` | Find files by pattern |
| `WebFetch` | Fetch and analyze web pages |
| `WebSearch` | Search the internet |

### Using Primitives in Agent Definitions

Add primitive tool names directly to the `tools` list alongside MCP tools:

```json
{
  "presentation_slide_writer": {
    "tools": [
      "mcp__custom-tools__list_slides",
      "mcp__custom-tools__generate_pptx",
      "Read",
      "Bash"
    ]
  }
}
```

### Key Principle

**Don't duplicate SDK primitives** with custom tools. Use custom MCP tools for domain-specific operations (like `add_slide`, `db_create_agent`), and SDK primitives for generic file/web/shell access.

---

## Agent Definition Schema

```json
{
  "agents": {
    "agent_id": {
      "name": "Human Readable Name",
      "description": "One-line description shown in `lightning list`",
      "system_prompt": "Full system prompt for the agent",
      "model": "haiku|sonnet",
      "tools": ["mcp__server__tool_name", ...],
      "created_at": "2024-12-01T00:00:00Z",
      "updated_at": "2024-12-01T00:00:00Z"
    }
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
- `mcp__custom-tools__download_pdf`
- `mcp__custom-tools__db_create_agent`

---

## Extending the System

### Adding a New Agent (Manual)

Edit `db/agents.json`:
```json
"my_agent": {
  "name": "My Agent",
  "description": "Does something useful",
  "system_prompt": "You are...",
  "model": "sonnet",
  "tools": [],
  "created_at": "2024-12-01T00:00:00Z",
  "updated_at": "2024-12-01T00:00:00Z"
}
```

Run it:
```bash
lightning run my_agent "Test prompt"
```

### Adding a New Agent (Architect)

```bash
lightning architect "agent that reviews code for memory leaks"
```

The architect uses CRUD tools to persist directly - no JSON parsing needed!

### Creating Custom Tools

```python
from claude_agent_sdk import tool

@tool("my_tool", "Does something", {"param": str})
async def my_tool(args):
    return {
        "content": [{"type": "text", "text": f"Result: {args['param']}"}]
    }
```

1. Add to `src/lightning_agents/tools/__init__.py`:
   ```python
   from .my_tool import my_tool
   # Add to custom_tools_server tools list
   ```

2. Register in `db/tools.json` (or use `tool_architect` agent)

3. Reference in agent definitions:
   ```json
   "tools": ["mcp__custom-tools__my_tool"]
   ```

---

## Troubleshooting

### "Agent not found"

```bash
lightning list          # Check available agents
lightning db list-agents  # Check database directly
```

### "MCP server failed"

Check `.env` has correct `SEARXNG_URL`.

### Import Errors

```bash
uv sync  # Reinstall dependencies
```

### "Tool not found"

```bash
lightning db list-tools  # Check registered tools
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

### 2. CRUD Tool Pattern

```python
@tool("db_create_agent", "Create a new agent", {...})
async def db_create_agent(args: dict) -> dict:
    # Validate, create, persist to db/agents.json
    return {"content": [{"type": "text", "text": "Created!"}]}
```

### 3. In-Process MCP Server

```python
# No subprocess needed - tools run in-process
custom_tools_server = create_sdk_mcp_server(
    name="custom-tools",
    tools=[my_tool, another_tool]
)
```

---

## Eat Your Own Cooking

**Always prefer using lightning-agents' own agents and tools** to accomplish tasks rather than doing things manually. This validates the system and helps it grow.

### Before Doing Work Manually

1. **Check existing agents**: `lightning list` - is there an agent for this?
2. **Check existing tools**: `lightning db list-tools` - is there a tool for this?
3. **If not, propose creating one** - the system should grow to handle new use cases

### Sub-Agent Pattern

Agents can invoke other agents via `mcp__custom-tools__run_agent`:

```
tool_architect → registers tool spec
    │
    └── run_agent(agent_id="tool_implementer", prompt="...")
            │
            └── tool_implementer writes the Python code
```

This enables Voyager-style autonomous capability growth.

### When to Create New Agents/Tools

| Scenario | Action |
|----------|--------|
| Repetitive task with specific domain | Create a new agent via `lightning architect` |
| Need a new capability for agents | Use `tool_architect` to design + implement |
| Agent needs to delegate specialized work | Add `run_agent` tool and create sub-agent |
| Complex workflow with multiple steps | Consider agent orchestration with sub-agents |

### Examples

```bash
# Need to work on slides? Use the slide agents
lightning run presentation_slide_writer "Add a new slide about X"
lightning run slides_checker "Review the presentation for issues"

# Need a new tool? Have tool_architect create it
lightning run tool_architect "Create a tool that does X"

# Need a new agent? Have architect create it
lightning architect "An agent that specializes in Y"
```

### Key Principle

**Don't do manually what an agent could do.** If no agent exists, create one. The system should become more capable over time through use.

---

## References

- [Claude Agent SDK Python](https://github.com/anthropics/claude-agent-sdk-python)
- [Anthropic API Docs](https://docs.anthropic.com)
- [NVIDIA Voyager Paper](https://arxiv.org/abs/2305.16291)
- [Austin AI MUG](https://aimug.org)
- [SearXNG](https://docs.searxng.org)
