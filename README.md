# Lightning Agents

**Dynamic agent instantiation using the Factory-of-Factories pattern with Claude Agent SDK.**

Built for the [Austin AI MUG](https://aimug.org) Lightning Talk.

---

## What is Lightning Agents?

Lightning Agents demonstrates a pattern for dynamically loading, instantiating, and even *generating* AI agents from declarative JSON definitions. Instead of hardcoding agent configurations, you define blueprints that get transformed into factory functions at runtime.

## The Problem

Building AI agents typically involves:
- Hardcoded system prompts scattered across files
- Tightly coupled agent definitions and execution logic
- No standardized way to add new agents without code changes
- Manual configuration duplication when agents share patterns

## The Solution

**Factory-of-Factories**: A registry that loads agent definitions from JSON, builds factory functions for each, and provides a unified interface for instantiation with runtime context injection.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Definition  │ ──▶ │   Factory   │ ──▶ │  Registry   │ ──▶ │  Instance   │
│   (JSON)    │     │  (Callable) │     │  (Unified)  │     │  (Ready)    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

---

## Quick Start

```bash
# Clone and setup
cd lightning-agents
uv sync

# Copy env template and configure
cp .env.example .env
# Edit .env with your SEARXNG_URL

# List available agents
lightning list

# Run an agent
lightning run basic_helper "What is the factory pattern?"

# Create a new agent with the architect
lightning architect "code reviewer for Python security"
```

---

## CLI Commands

### List Agents

```bash
lightning list
```

Shows all available agents with descriptions and model info.

### Run Agent

```bash
lightning run <agent_id> "<prompt>"
```

Examples:
```bash
lightning run basic_helper "Explain dependency injection"
lightning run aimug_researcher "What RAG tutorials does AIMUG have?"
lightning run lab_finder "Find labs about LangGraph"
```

### Create New Agent

```bash
lightning architect "<task description>"
```

The architect agent generates a new agent definition, saves it to `agents.json`, and makes it immediately available.

```bash
lightning architect "meeting notes summarizer for action items"
# New agent created: meeting_summarizer
lightning run meeting_summarizer "Summarize: [transcript]"
```

---

## Available Agents

| Agent | Description | Model |
|-------|-------------|-------|
| `basic_helper` | General Q&A assistant | haiku |
| `research_assistant` | Structured research summaries | sonnet |
| `python_doc_writer` | Python function documentation | haiku |
| `architect` | Designs new agent definitions | sonnet |
| `aimug_researcher` | Searches AIMUG content (GitHub, docs, YouTube) | sonnet |
| `lab_finder` | Finds AIMUG labs by topic | haiku |

---

## Factory vs Factory-of-Factories

### Simple Factory
```python
def create_agent(config):
    return Agent(config)
```

### Factory-of-Factories (This Project)
```python
# Definition → Factory → Registry → Instance
registry = AgentRegistry.from_json("agents.json")  # Builds ALL factories
agent = registry.create("researcher", {"topic": "AI"})  # Gets instance
```

The registry *is* the factory-of-factories — it produces factory functions from definitions, then uses those factories to produce instances.

---

## Architect Agents

The "Architect Agent" pattern: **an agent that generates new agent definitions**.

```bash
# Before: 6 agents
lightning list

# Use architect to create a new one
lightning architect "code reviewer for security vulnerabilities"

# After: 7 agents - new one saved to agents.json
lightning list

# Use it immediately
lightning run security_reviewer "Review this auth code..."
```

This enables self-expanding agent systems where the AI itself designs specialized agents for new tasks.

---

## Hypotheses

### H1: Declarative > Imperative for Agent Configuration
JSON definitions separate *what* an agent is from *how* it runs. Easier to version, diff, and review.

### H2: Runtime Context Injection Enables Reusability
The same definition can serve multiple contexts by injecting different runtime parameters.

### H3: Architect Agents Enable Organic Growth
Instead of manually writing every agent definition, let Claude design agents for new tasks. The system grows based on actual needs.

---

## Project Structure

```
lightning-agents/
├── .env.example              # Environment template
├── .env                      # Your config (gitignored)
├── pyproject.toml
├── README.md
├── CLAUDE.md                 # Developer notes
├── src/lightning_agents/     # Main package
│   ├── __init__.py
│   ├── agents.json           # Agent blueprints (6 agents)
│   ├── cli.py                # CLI entry point
│   ├── runner.py             # Agent execution with MCP
│   ├── registry.py           # Factory-of-Factories pattern
│   ├── agent_factory.py      # Definition → Instance
│   └── mcp_config.py         # MCP server configs
└── presentation/             # PPTX slide generator
    ├── generate_slides.py
    ├── slide_content.py
    └── styles.py
```

---

## Generating Slides

```bash
# Install presentation deps
uv sync --extra presentation

# Generate PPTX
uv run python -m presentation.generate_slides

# Output: presentation/output/lightning-agents.pptx
```

Edit `presentation/slide_content.py` to update content, then regenerate.

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# SearXNG MCP server URL (for web search agents)
SEARXNG_URL=http://localhost:8888
```

### MCP Tools

Agents can use MCP tools by declaring them in their `tools` array:
- `mcp__searxng__searxng_web_search` - Web search
- `mcp__searxng__web_url_read` - Read web page content

---

## Requirements

- Python 3.13+
- `uv` package manager
- SearXNG instance (for search-enabled agents)

---

## License

MIT

---

*Built for the Austin AI MUG lightning talk on dynamic agent instantiation patterns.*
