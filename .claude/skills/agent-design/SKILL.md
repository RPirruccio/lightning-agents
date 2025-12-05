---
name: agent-design
description: Use when designing new agents for Lightning Agents. Covers AGENT.md schema, dependencies, skills, and Voyager patterns.
---

# Agent Design

A skill for designing effective agents in the Lightning Agents framework.

## Agent Storage: AGENT.md Format

Agents are stored as `.claude/agents/<agent_id>/AGENT.md`:

```yaml
---
name: Human Readable Name
description: One-line description for `lightning list`
model: haiku  # or sonnet
tools:
- Read
- Edit
- Bash
- mcp__custom-tools__some_tool
skills:
- skill-id
subagents:
- other_agent_id
created_at: '2024-12-01T00:00:00Z'
updated_at: '2024-12-01T00:00:00Z'
---

You are a helpful agent that...

## Your Capabilities
...system prompt continues as markdown...
```

## Complete Agent Creation Workflow

### 1. Check Dependencies

If agent needs external tools:

```bash
# Read current dependencies
Read pyproject.toml

# Add new dependency
Edit pyproject.toml:
  "vulture>=2.10",  # Dead code detection
  "ruff>=0.4.0",    # Fast linting
  "black>=24.0",    # Formatting
  "mypy>=1.0",      # Type checking

# Install
Bash: uv sync
```

### 2. Create Skill (If Needed)

For reusable domain expertise:

```bash
# Create skill directory and file
mkdir -p .claude/skills/<skill-id>
# Write SKILL.md with frontmatter + content
```

Or use `db_create_skill` tool.

### 3. Create Agent

Use `db_create_agent` tool with:
- `agent_id`: snake_case identifier
- `name`: Human readable name
- `description`: One-line summary
- `model`: haiku or sonnet
- `tools`: List of tool names
- `skills`: List of skill IDs
- `subagents`: List of agent IDs
- `system_prompt`: Full prompt

## Model Selection

| Model | Use For | Cost/Speed |
|-------|---------|------------|
| `haiku` | Formatting, classification, simple checks | Fast, cheap |
| `sonnet` | Reasoning, code gen, multi-step workflows | Slower, smarter |

**Default to haiku** unless you need:
- Complex reasoning chains
- Code generation
- Creative/analytical tasks

## Tool Categories

### SDK Primitives (built-in)
```yaml
tools:
- Read      # Read files
- Write     # Create files
- Edit      # Modify files
- Bash      # Run shell commands
- Grep      # Search content
- Glob      # Find files
- WebFetch  # Fetch URLs
- WebSearch # Search web
```

### Custom MCP Tools
```yaml
tools:
- mcp__custom-tools__db_list_agents
- mcp__custom-tools__db_create_agent
- mcp__searxng__searxng_web_search
```

## Skills vs Subagents

| Aspect | Skills | Subagents |
|--------|--------|-----------|
| Purpose | Add knowledge to agent | Delegate work to specialist |
| Context | Loaded INTO parent | Separate context window |
| Execution | Parent does work | Subagent does work |
| Use When | Need procedures, domain knowledge | Need isolated execution |

## Common Agent Patterns

### Code Analyzer
```yaml
model: sonnet
tools: [Read, Grep, Bash]
skills: [relevant-coding-skill]
```
Uses external tools via Bash (vulture, ruff, mypy).

### Formatter/Fixer
```yaml
model: haiku
tools: [Read, Edit]
```
Simple transformations, no complex reasoning.

### Orchestrator
```yaml
model: sonnet
tools: [Read, Bash]
subagents: [worker_agent_1, worker_agent_2]
```
Coordinates specialist subagents.

### Researcher
```yaml
model: sonnet
tools: [mcp__searxng__searxng_web_search, mcp__searxng__web_url_read]
```
Web research and synthesis.

## Validation Checklist

Before creating an agent:

- [ ] ID is snake_case and descriptive
- [ ] Dependencies added to pyproject.toml and installed
- [ ] Skills created if agent needs domain knowledge
- [ ] Model matches task complexity
- [ ] Tools are minimal but sufficient
- [ ] System prompt has: role, capabilities, workflow, output format
- [ ] No duplicate with existing agents

## Testing

```bash
# Create via architect
lightning architect "description of agent"

# Or run directly if manually created
lightning run agent_id "test prompt"

# Check agent was created
lightning db get-agent agent_id
```
