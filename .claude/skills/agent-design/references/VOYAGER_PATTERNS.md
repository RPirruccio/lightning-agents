# Voyager Patterns in Lightning Agents

Inspired by NVIDIA's Voyager paper (arXiv:2305.16291), Lightning Agents implements a self-modifying skill library for autonomous capability growth.

## Core Concept

**Voyager** is an AI agent that learns to play Minecraft by:
1. Maintaining a **skill library** (reusable code functions)
2. **Adding new skills** when facing new challenges
3. **Composing skills** to accomplish complex tasks
4. **Growing organically** without pre-programmed behaviors

**Lightning Agents** mirrors this with:
1. Agent definitions stored in `db/agents.json` (skill library)
2. CRUD tools to create/modify agents (self-modification)
3. Sub-agent delegation via `run_agent` tool (composition)
4. Organic growth based on actual user needs

## Pattern 1: Self-Modifying Skill Library

### Voyager Approach
```python
# Voyager saves new skills as code
skill_library["mine_wood"] = """
def mine_wood(bot):
    tree = bot.findBlock('oak_log')
    bot.dig(tree)
    bot.collectDrops()
"""
```

### Lightning Agents Approach
```python
# Lightning Agents saves new agents as JSON
db_create_agent({
    "agent_id": "code_reviewer",
    "system_prompt": "You review code...",
    "tools": ["Read", "Grep"]
})
```

### Key Similarity
Both systems can **create new capabilities at runtime** without human intervention.

### Implementation in Lightning

The `architect` agent has CRUD tools:
- `db_list_agents` - See what exists
- `db_get_agent` - Retrieve details
- `db_create_agent` - **Persist new agent**

When you run:
```bash
lightning architect "agent that reviews Python imports"
```

The architect:
1. Lists existing agents to avoid duplicates
2. Designs the new agent
3. **Calls `db_create_agent` directly**
4. Agent is immediately available

## Pattern 2: Skill Composition

### Voyager Approach
```python
# Complex skill built from simpler skills
def build_house(bot):
    mine_wood(bot)      # Skill 1
    craft_planks(bot)   # Skill 2
    place_walls(bot)    # Skill 3
```

### Lightning Agents Approach
```python
# Orchestrator agent delegates to sub-agents
slides_quality_loop:
  1. run_agent("slides_checker", "analyze PDF")
  2. Parse feedback
  3. run_agent("presentation_slide_writer", "fix issues")
  4. Repeat
```

### Implementation in Lightning

Agents with `run_agent` tool can delegate:

```json
{
  "slides_quality_loop": {
    "tools": [
      "mcp__custom-tools__run_agent",
      "Read",
      "Bash"
    ],
    "system_prompt": "You orchestrate presentation improvement by chaining slides_checker and presentation_slide_writer..."
  }
}
```

## Pattern 3: Progressive Capability Growth

### Voyager Learning Curve

```
Day 1: Learn to mine wood
Day 2: Learn to craft tools (using wood skill)
Day 3: Learn to mine stone (using tool skill)
Day 4: Learn to build shelter (using all previous skills)
```

### Lightning Agents Growth Curve

```
Phase 1: Basic agents (helper, researcher)
Phase 2: Meta agents (architect creates new agents)
Phase 3: Orchestration (quality_loop chains agents)
Phase 4: Tool creation (tool_architect + tool_implementer)
```

### Eat Your Own Cooking Principle

**Instead of manually coding**:
```bash
# Manual: vim src/new_feature.py
```

**Use agents to grow the system**:
```bash
lightning architect "agent that implements new features"
lightning run feature_implementer "add authentication"
```

This validates the system AND makes it more capable over time.

## Pattern 4: Curriculum Learning

### Voyager Approach

Uses GPT-4 to:
1. Suggest next achievable goal
2. Attempt goal using existing skills
3. Create new skill if needed
4. Add skill to library for future use

### Lightning Agents Approach

User-driven curriculum:
1. User identifies need (e.g., "I need better slide reviews")
2. Check existing agents: `lightning list`
3. If gap exists, create agent: `lightning architect "slides quality loop"`
4. Agent is immediately usable for this and future tasks

### Future: Autonomous Curriculum

Potential enhancement:
```json
{
  "meta_learner": {
    "tools": [
      "db_list_agents",
      "db_create_agent",
      "run_agent"
    ],
    "system_prompt": "You analyze user requests, identify capability gaps, and proactively create agents to fill them..."
  }
}
```

## Pattern 5: Skill Retrieval

### Voyager Approach

Uses vector embeddings to find relevant skills:
```python
query = "I need to build a crafting table"
relevant_skills = skill_library.search(query)
# Returns: ["mine_wood", "craft_planks", "craft_table"]
```

### Lightning Agents Current Approach

Simple text-based listing:
```bash
lightning list  # Shows all agents with descriptions
```

### Future Enhancement

Could add semantic search:
```python
db_search_agents(query="improve presentations")
# Returns: ["slides_checker", "slides_quality_loop", "presentation_slide_writer"]
```

## Key Differences from Voyager

| Aspect | Voyager | Lightning Agents |
|--------|---------|------------------|
| Domain | Minecraft gameplay | General-purpose tasks |
| Skills | Python code | Agent definitions |
| Storage | In-memory + file | JSON database |
| Execution | Direct code execution | Claude API calls |
| Composition | Function calls | Sub-agent delegation |
| Curriculum | Autonomous exploration | User-driven + meta-agents |

## Applying Voyager Principles

### 1. When Designing New Agents

**Think**: Could this agent create OTHER agents?

Example:
- `architect` creates general agents
- `tool_architect` creates tools + delegates implementation

### 2. When Building Complex Workflows

**Think**: Can I compose existing agents instead of writing code?

Example:
```python
# Instead of writing orchestration code
quality_loop = """
1. Check slides
2. Parse feedback
3. Fix issues
4. Regenerate
"""

# Create an orchestrator agent that uses existing agents
slides_quality_loop → slides_checker + presentation_slide_writer
```

### 3. When Identifying Gaps

**Think**: Should I create a specialized agent for this recurring task?

Example:
- User keeps asking for code reviews → Create `code_reviewer` agent
- User needs icons downloaded → Create `find_icon` tool

### 4. When Measuring Success

**Think**: Is the system becoming more capable over time?

Metrics:
- Number of agents in db/agents.json (skill library size)
- Frequency of agent creation (learning rate)
- Agent reuse across tasks (skill composition)
- Reduced manual intervention (autonomy)

## References

- [Voyager Paper](https://arxiv.org/abs/2305.16291) - Original NVIDIA research
- [Voyager GitHub](https://github.com/MineDojo/Voyager) - Implementation
- CLAUDE.md - Lightning Agents architecture
- db/agents.json - Current skill library
