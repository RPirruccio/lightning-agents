---
name: use-architect
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.claude/(agents|skills)/
action: block
---

🛑 **BLOCKED: Manual agent/skill creation detected**

You're trying to write directly to `.claude/agents/` or `.claude/skills/`.

**Use the proper tools instead:**

```bash
# Create an agent via architect
lightning architect "description of agent"

# Or use CRUD tools if you're an agent:
mcp__custom-tools__db_create_agent
mcp__custom-tools__db_create_skill
```

**Why?**
- Architect handles dependencies (pyproject.toml, uv sync)
- Architect creates skills when needed
- Eat your own cooking - validate the system works

**The architect agent has:**
- `db_create_agent` - writes AGENT.md
- `db_create_skill` - writes SKILL.md
- `Read`, `Edit`, `Bash` - manages dependencies
