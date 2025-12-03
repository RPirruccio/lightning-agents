# LangGraph Evolution & Deep Agents Research

**Date**: 2024-12-03
**Context**: Lightning talk preparation for Austin AI MUG

---

## LangGraph Evolution

LangGraph has progressed through several paradigms:

### 1. Graph API (Original)
- Explicit nodes, edges, state transitions
- `StateGraph` class with `compile()`
- Very structured, directed graph thinking
- Requires mapping out entire flow upfront

### 2. Functional API (Newer)
- Uses `@entrypoint` and `@task` decorators
- More Pythonic, less rigid structure
- Standard control flow (if, for, function calls)
- State scoped to functions

### 3. create_react_agent (Factory Pattern)
- Prebuilt ReAct agent factory
- Pass config, get agent - essentially a factory pattern
- Memory via `checkpointer` (short-term) and `store` (long-term)
- Has hooks (pre_model_hook, post_model_hook)

### 4. Deep Agents (Latest - July 2025)
- New paradigm inspired by Claude Code, Manus, Deep Research
- Built on LangGraph but more context-driven than programmatic
- Package: `pip install deepagents`

---

## Deep Agents: Four Key Characteristics

From the official LangChain blog (blog.langchain.com/deep-agents/):

### 1. Detailed System Prompt
- Long prompts with instructions and few-shot examples
- Claude Code's prompts are thousands of lines
- "Prompting matters still!"

### 2. Planning Tool
- Todo list tool that's basically a **no-op**
- Doesn't actually do anything - just context engineering
- Keeps the agent on track over longer tasks

### 3. Sub Agents
- Ability to spawn specialized sub-agents
- Split up tasks, each sub-agent goes deep on its area
- Custom sub-agents for specific domains

### 4. File System
- Virtual file system for storing notes/context
- Shared workspace for all agents to collaborate
- Memory management for long-running tasks
- Manus also uses this pattern heavily

---

## Connection to Lightning Agents

Lightning Agents implements similar patterns:

| Deep Agents Concept | Lightning Agents Implementation |
|---------------------|--------------------------------|
| File System | `db/` folder with `agents.json`, `tools.json` |
| Sub Agents | `architect` creates new agents on demand |
| Tool Creation | `tool_architect` creates new tools |
| Persistence | Real JSON files (survives sessions) |
| Registry | Factory-of-Factories pattern |

**Key Difference**: Deep Agents uses virtual file system in agent state. Lightning Agents uses real persistent JSON files - arguably more powerful for true persistence.

---

## Voyager Connection

The Voyager paper (Minecraft AI) introduced "skill library" concept:
- Learns new skills → stores them → reuses them
- Skills compound over time
- System grows based on actual needs

Lightning Agents applies this:
- Agents stored as reusable definitions (skill library → agent registry)
- Architect creates new agents (learning → creating)
- Tool architect creates tools (skill acquisition)

---

## Presentation Narrative

**For AIMUG (Sovereign AI focus)**:

1. **LangGraph Evolution**: Graph API → Functional API → create_react_agent → Deep Agents
2. **The Trend**: More declarative, less code, more context-driven
3. **Factory-of-Factories**: Pattern that enables self-expanding systems
4. **Lightning Agents**: One implementation that demonstrates:
   - Agents creating agents
   - Agents creating tools
   - Real persistence (not just in-memory)
   - Claude Agent SDK = own everything, run locally

**Value Prop**: LangGraph gives you primitives. Deep Agents shows direction. Lightning Agents shows how Factory-of-Factories makes self-expanding systems natural.

---

## Sources

- LangGraph Docs: docs.langchain.com/langgraph
- Deep Agents Blog: blog.langchain.com/deep-agents/
- Deep Agents GitHub: github.com/langchain-ai/deepagents
- DeepWiki LangGraph: deepwiki.com search results
- Voyager Paper: arxiv.org/abs/2305.16291
