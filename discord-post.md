# ⚡ Lightning Agents - Austin AI MUG Lightning Talk ⚡

Just finished building the demo for my lightning talk! It's a CLI tool that shows how to dynamically create AI agents from JSON definitions using the Factory-of-Factories pattern.

The cool part: there's an "architect" agent that generates new agents on the fly. You literally ask it "make me a code reviewer" and boom - new agent added to the system, ready to use immediately.

The whole thing got pretty meta - I used the architect to create a `git_commit_writer` agent, then used *that* to write all the commits in the repo. Even made an agent to generate the presentation slides!

Built with Claude Agent SDK + MCP for tool integration.

```
lightning list              # see all agents
lightning run <agent> "..." # use an agent
lightning architect "..."   # create a new agent
```

**PDF slides:** <https://github.com/RPirruccio/lightning-agents/blob/main/presentation/output/lightning-agents.pdf>

**Repo:** <https://github.com/RPirruccio/lightning-agents>

Agents creating agents 🤖➡️🤖

---

# Follow-up: just tested the agents on real AIMUG content

Asked it to find good labs from Karim using the `aimug_researcher` and `lab_finder` agents. Here's what came back:

**Karim's top projects by GitHub stars:**

- **WebRTC AI Voice Chat** ⭐ 140 - Voice chat with LLMs, get audio responses
- **AI Chatbot with RAG** ⭐ 43 - Full RAG setup, scrapes sites/PDFs into knowledge base
- **Tool Calling LLM** ⭐ 32 - Adds `.bind_tools()` to any LangChain model
- **Style Guide AI** ⭐ 15 - Voice-enabled fashion assistant with vision

The RAG chatbot is probably the best starting point if you're learning: <https://github.com/lalanikarim/ai-chatbot-rag>

The Style Guide one is wild though - voice + vision + weather-aware outfit recommendations. There's a demo: <https://www.youtube.com/watch?v=aWYGDufOR_k>

Both agents used MCP web search under the hood to pull this info. Pretty cool seeing them actually work on real queries 🤙

---

# How it works under the hood

Those results came from two agents defined in `agents.json`. Here's what they look like:

**aimug_researcher** (sonnet + 2 MCP tools):
```json
{
  "name": "AIMUG Researcher",
  "description": "Searches and synthesizes info from Austin LangChain resources",
  "system_prompt": "You are an AIMUG Research Assistant... [includes GitHub repo structure, docs site, YouTube channel, search strategy instructions]",
  "model": "sonnet",
  "tools": [
    "mcp__searxng__searxng_web_search",
    "mcp__searxng__web_url_read"
  ]
}
```

**lab_finder** (haiku + 1 MCP tool):
```json
{
  "name": "AIMUG Lab Finder",
  "description": "Finds specific Austin LangChain labs by topic",
  "system_prompt": "You are the AIMUG Lab Finder... [includes full lab catalog from 101-111+]",
  "model": "haiku",
  "tools": ["mcp__searxng__searxng_web_search"]
}
```

The system prompts have domain knowledge baked in (repo structure, lab catalog, search strategies) so they know where to look.

These were hand-written in `agents.json`, but the other agents like `git_commit_writer` were created dynamically using:
```
lightning architect "git commit message writer that follows conventional commits"
```

The architect reads your description, generates the JSON config, and adds it to the registry. No code changes needed.

That's the whole point of the Factory-of-Factories pattern - agents are just data. Define them in JSON, load them at runtime, create new ones on the fly 🔧
