"""
Slide content definitions.

Edit this file to update presentation content.
Run `uv run python -m presentation.generate_slides` to regenerate.
"""

SLIDES = [
    {
        "type": "title",
        "title": "⚡ Lightning Agents ⚡",
        "subtitle": "Factory-of-Factories for Dynamic AI Agents",
        "presenter": "Riccardo Pirruccio",
        "footer": "github.com/RPirruccio/lightning-agents | aimug.org",
    },
    {
        "type": "before_after",
        "title": "The Problem & Solution",
        "before_title": "❌ TYPICAL AGENT CODE",
        "before_items": [
            "agent_v1.py, agent_v2.py, agent_final.py...",
            "Hardcoded prompts in every file",
            "Copy-paste to create new agents",
            "Change model name in 47 places",
            "No single source of truth",
        ],
        "after_title": "✅ FACTORY-OF-FACTORIES",
        "after_items": [
            "One agents.json (single source of truth)",
            "Declarative definitions",
            "Registry builds factories",
            "Runtime context injection",
            "Agents create new agents",
        ],
    },
    {
        "type": "comparison",
        "title": "The Voyager Insight",
        "left_header": "🎮 VOYAGER (Minecraft AI)",
        "left_color": "text_light",
        "right_header": "⚡ LIGHTNING AGENTS",
        "right_color": "secondary",
        "rows": [
            ("Learns new skill", "Creates new agent"),
            ("Stores in skill library", "Stores in agents.json"),
            ("Retrieves skill when needed", "Retrieves agent via Registry.create()"),
            ("Skills compound over time", "Agents create agents over time"),
        ],
        "footer": "SAME PATTERN. DIFFERENT DOMAIN.",
    },
    {
        "type": "convergence",
        "title": "The Industry Agrees",
        "sources": [
            {"label": "Voyager", "image": "voyager.png"},
            {"label": "LangGraph", "image": "langgraph.png"},
            {"label": "Deep Agents", "image": "deep_agents.png"},
            {"label": "Claude Agent SDK", "image": "claude_sdk.png"},
        ],
        "target": "Factory-of-Factories:\nAgents that create agents\nfrom declarative configs",
        "footer": "Everyone's arriving at the same place: less code, more context engineering",
    },
    {
        "type": "diagram",
        "title": "The Solution: Factory-of-Factories",
        "diagram_id": "main_flow",
        "footer": "① Load → ② Parse → ③ Build Factory → ④ Instantiate with Context",
    },
    {
        "type": "code_comparison",
        "title": "Simple Factory vs Factory-of-Factories",
        "left_title": "Simple Factory",
        "left_code": "# One factory, one agent type\ndef create_agent(config):\n    return Agent(config)\n\n# Each new agent = new factory",
        "right_title": "Factory-of-Factories",
        "right_code": "# Registry builds factories dynamically\nregistry = AgentRegistry.from_json(\n    \"agents.json\"\n)\nagent = registry.create(\n    \"researcher\", {\"topic\": \"AI\"}\n)\n# Any agent from one registry!",
    },
    {
        "type": "code",
        "title": "Declarative Agent Definition",
        "code": '''{
  "architect": {
    "name": "Agent Architect",
    "description": "Designs new agents",
    "system_prompt": "You are an Agent Architect...",
    "model": "sonnet",
    "tools": [
      "mcp__custom-tools__db_create_agent",
      "mcp__custom-tools__db_list_agents",
      "mcp__custom-tools__run_agent"
    ]
  }
}''',
        "bullets": [
            "**JSON, not code** — agents defined declaratively in agents.json",
            "**Context engineering** — the system_prompt is where the magic happens",
            "**Composable tools** — agents can invoke other agents via run_agent",
        ],
    },
    {
        "type": "code",
        "title": "The Registry Pattern",
        "code": '''class AgentRegistry:
    def from_json(path) -> "AgentRegistry":
        # Load definitions -> build factories

    def create(id, opts) -> AgentInstance:
        # Factory creates configured instance

    def register(id, defn) -> None:
        # Add new agent to registry''',
        "bullets": [
            "**Single source of truth** — all agent definitions in one place",
            "**Runtime creation** — agents spawn new agents on demand",
            "**Self-modifying** — architects can register new agents dynamically",
        ],
    },
    {
        "type": "diagram",
        "title": "The Architect Agent",
        "diagram_id": "architect_flow",
    },
    {
        "type": "diagram",
        "title": "Introducing: The Tool Architect",
        "diagram_id": "tool_architect_flow",
    },
    {
        "type": "code",
        "title": "Demo: What We Built",
        "code": '''$ lightning list
  10 agents: architect, tool_architect, paper_researcher...

$ lightning run paper_researcher "Find the Voyager paper"
  Found: arxiv.org/abs/2305.16291
  Downloaded: voyager_lifelong_learning.pdf

$ lightning run presentation_slide_writer "List slides"
  12 slides in current presentation...''',
        "bullets": [
            "`lightning list` — show all agents in the registry",
            "`lightning run <agent>` — invoke any agent with natural language",
            "**10+ agents** all from one `agents.json` file",
        ],
    },
    {
        "type": "bullets",
        "title": "The Meta Moment 🤯",
        "bullets": [
            "We used `paper_researcher` to find the **Voyager paper**",
            "Voyager inspired the **architect pattern**",
            "We built `tool_architect` to create **more tools**",
            "`presentation_slide_writer` built **THIS presentation**",
            "**Agents all the way down:** Architect → Slide Writer → This Slide",
        ],
    },
    {
        "type": "closing",
        "title": "⚡ Lightning Agents ⚡",
        "bullets": [
            "**Questions?**",
            "**Agents** creating **agents** creating **tools**",
            "Built with `Claude Agent SDK` + `MCP`",
            "📦 **This project:** `github.com/RPirruccio/lightning-agents`",
            "🤝 **AIMUG community:** `github.com/aimug-org/austin_langchain`",
        ],
        "footer": "github.com/RPirruccio/lightning-agents",
    },
]

# Diagram definitions for visual slides
DIAGRAMS = {
    "main_flow": {
        "boxes": [
            {"label": "agents.json", "x": 1.5, "y": 2.6, "color": "primary", "desc": "Single source of truth"},
            {"label": "Definition", "x": 4.5, "y": 2.6, "color": "primary", "desc": "JSON with prompt, model, tools"},
            {"label": "Factory", "x": 7.5, "y": 2.6, "color": "secondary", "desc": "Creates configured instances"},
            {"label": "Instance", "x": 10.5, "y": 2.6, "color": "success", "desc": "Ready to run with context"},
        ],
        "arrows": [(0, 1), (1, 2), (2, 3)],
    },
    "architect_flow": {
        "boxes": [
            {"label": "Task\nDescription", "x": 0.8, "y": 2.2, "color": "text_light"},
            {"label": "Architect Agent", "x": 3.8, "y": 1.8, "color": "secondary", "subtitle": "🏗️ The agent that creates agents", "large": True},
            {"label": "New Agent\nDefinition", "x": 8.0, "y": 2.2, "color": "primary"},
            {"label": "Registry", "x": 3.8, "y": 5.0, "color": "primary"},
            {"label": "New Agent\nInstance", "x": 8.0, "y": 5.0, "color": "success"},
        ],
        "arrows": [(0, 1), (1, 2), (2, 3), (3, 4)],
        "arrow_labels": ["Receives", "Generates", "Persists", "Spawns"],
        "feedback_loop": {
            "from_idx": 4,
            "to_idx": 3,
            "label": "Can now create\nagents too!",
            "color": "secondary",
        },
        "footer": "🤔 What happens when created agents can also create agents?",
    },
    "tool_architect_flow": {
        "boxes": [
            {"label": "Tool\nRequest", "x": 0.3, "y": 2.8, "color": "text_light"},
            {"label": "tool_architect", "x": 2.8, "y": 2.8, "color": "secondary", "subtitle": "🤖 Designs"},
            {"label": "tools.json", "x": 5.3, "y": 2.8, "color": "primary", "is_database": True},
            {"label": "tool_implementer", "x": 7.8, "y": 2.8, "color": "secondary", "subtitle": "🤖 Builds"},
        ],
        "arrows": [(0, 1), (1, 2), (2, 3)],
        "arrow_labels": ["spec", "saves", "reads"],
        "result_box": {"label": "New Tool\nAvailable", "x": 7.8, "y": 5.2, "color": "success"},
        "result_arrow": (3, "result"),
        "result_arrow_label": "deploys",
        "feedback_loop": {
            "from_result": True,
            "to_label": "System",
            "label": "Now available\nsystem-wide",
            "color": "success",
        },
        "footer": "🤯 Agents creating tools for other agents to use",
    },
}
