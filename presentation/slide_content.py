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
        "presenter": "Ricardo Pirruccio",
        "footer": "github.com/RPirruccio/lightning-agents | aimug.org",
    },
    {
        "type": "before_after",
        "title": "Before & After",
        "before_title": "TYPICAL AGENT CODE",
        "before_items": [
            "agent_v1.py, agent_v2.py, agent_final.py...",
            "Hardcoded prompts in every file",
            "Copy-paste to create new agents",
            "Change model name in 47 places",
            "No single source of truth",
        ],
        "after_title": "FACTORY-OF-FACTORIES",
        "after_items": [
            "One agents.json file",
            "Declarative definitions",
            "Registry builds factories",
            "Runtime context injection",
            "Agents create new agents",
        ],
    },
    {
        "type": "comparison",
        "title": "The Voyager Insight",
        "left_header": "VOYAGER (2023)",
        "left_color": "text_light",
        "right_header": "LIGHTNING AGENTS",
        "right_color": "secondary",
        "rows": [
            ("Learns new skill", "Creates new agent"),
            ("Stores in skill library", "Stores in agents.json"),
            ("Retrieves when needed", "Registry.create()"),
            ("Skills compound over time", "Agents create agents"),
        ],
        "footer": "SAME PATTERN. DIFFERENT DOMAIN.",
    },
    {
        "type": "convergence",
        "title": "The Industry Agrees",
        "sources": [
            {"label": "Voyager (2023)", "image": "voyager.png"},
            {"label": "LangGraph", "image": "langgraph.png"},
            {"label": "Deep Agents", "image": "deep_agents.png"},
            {"label": "Claude Agent SDK", "image": "claude_sdk.png"},
        ],
        "target": "Factory-of-Factories",
        "footer": "Everyone's arriving at the same place: less code, more context engineering",
    },
    {
        "type": "diagram",
        "title": "The Solution: Factory-of-Factories",
        "diagram_id": "main_flow",
    },
    {
        "type": "code_comparison",
        "title": "Simple Factory vs Factory-of-Factories",
        "left_title": "Simple Factory",
        "left_code": "def create_agent(config):\n    return Agent(config)",
        "right_title": "Factory-of-Factories",
        "right_code": "registry = AgentRegistry.from_json(\n    \"agents.json\"\n)\nagent = registry.create(\n    \"researcher\", {\"topic\": \"AI\"}\n)",
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
            "**Single source of truth** for all agent definitions",
            "**Runtime creation** - agents spawn new agents on demand",
            "**Self-modifying** - architects can register new agents",
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
    },
    {
        "type": "bullets",
        "title": "The Meta Moment",
        "bullets": [
            "We used `paper_researcher` to find the **Voyager paper**",
            "Voyager inspired the **architect pattern**",
            "We built `tool_architect` to create **more tools**",
            "`presentation_slide_writer` built **THIS presentation**",
            "**This slide** was created by an agent that was created by an agent",
        ],
    },
    {
        "type": "closing",
        "title": "⚡ Lightning Agents ⚡",
        "bullets": [
            "**Questions?**",
            "**Agents** creating **agents** creating **tools**",
            "Built with `Claude Agent SDK` + `MCP`",
            "`github.com/aimug-org/austin_langchain`",
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
            {"label": "Task\nDescription", "x": 1.5, "y": 2.5, "color": "text_light"},
            {"label": "Architect\nAgent", "x": 5.0, "y": 2.5, "color": "secondary"},
            {"label": "New Agent\nDefinition", "x": 8.5, "y": 2.5, "color": "primary"},
            {"label": "Registry", "x": 5.0, "y": 4.8, "color": "primary"},
            {"label": "New Agent\nInstance", "x": 8.5, "y": 4.8, "color": "success"},
        ],
        "arrows": [(0, 1), (1, 2), (2, 3), (3, 4), (2, 3)],
        "back_arrow": {"from": 2, "to": 3},  # Definition back to Registry (self-modifying cycle)
    },
    "tool_architect_flow": {
        "boxes": [
            {"label": "Tool\nRequest", "x": 1.0, "y": 3.2, "color": "text_light"},
            {"label": "tool_architect", "x": 4.0, "y": 3.2, "color": "secondary"},
            {"label": "db/tools.json", "x": 7.0, "y": 3.2, "color": "primary"},
            {"label": "tool_implementer", "x": 10.0, "y": 3.2, "color": "secondary"},
        ],
        "arrows": [(0, 1), (1, 2), (2, 3)],
        "result_box": {"label": "New Tool\nAvailable", "x": 10.0, "y": 5.2, "color": "success"},
        "result_arrow": (3, "result"),
    },
}
