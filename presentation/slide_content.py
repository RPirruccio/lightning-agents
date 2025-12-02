"""
Slide content definitions.

Edit this file to update presentation content.
Run `uv run python -m presentation.generate_slides` to regenerate.
"""

SLIDES = [
    {
        "type": "title",
        "title": "Lightning Agents",
        "subtitle": "Factory-of-Factories for Dynamic AI Agents",
        "footer": "Austin AI MUG Lightning Talk",
    },
    {
        "type": "bullets",
        "title": "The Problem",
        "bullets": [
            "**Hardcoded** system prompts scattered across files",
            "**Tightly coupled** agent definitions and execution logic",
            "No standardized way to add agents **without code changes**",
            "Manual **configuration duplication** when agents share patterns",
        ],
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
    "tools": []
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
    },
    {
        "type": "bullets",
        "title": "The Voyager Insight",
        "bullets": [
            "**Voyager**: Minecraft AI with a growing **skill library**",
            "Learns new skills → **stores them** → reuses them",
            "**Lightning Agents**: same pattern for AI agents",
            "`architect` creates → `Registry` stores → `CLI` runs",
        ],
    },
    {
        "type": "diagram",
        "title": "The Architect Agent",
        "diagram_id": "architect_flow",
    },
    {
        "type": "bullets",
        "title": "But Wait... Tool Architect Too",
        "bullets": [
            "Agents can also design **NEW TOOLS**",
            "`tool_architect` registers definitions in `db/tools.json`",
            "`paper_researcher` searches papers **AND** downloads PDFs",
            "`presentation_slide_writer` manipulates slides **directly**",
        ],
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
            "`presentation_slide_writer` is building **THIS presentation**",
        ],
    },
    {
        "type": "closing",
        "title": "Lightning Agents",
        "bullets": [
            "**Agents** creating **agents** creating **tools**",
            "Built with `Claude Agent SDK` + `MCP`",
            "`github.com/aimug-org/lightning-agents`",
        ],
        "footer": "Austin AI MUG | aimug.org",
    },
]

# Diagram definitions for visual slides
DIAGRAMS = {
    "main_flow": {
        "boxes": [
            {"label": "Definition\n(JSON)", "x": 1.5, "y": 3.2, "color": "primary"},
            {"label": "Factory\n(Callable)", "x": 4.5, "y": 3.2, "color": "primary"},
            {"label": "Registry\n(Unified)", "x": 7.5, "y": 3.2, "color": "secondary"},
            {"label": "Instance\n(Ready)", "x": 10.5, "y": 3.2, "color": "success"},
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
        "arrows": [(0, 1), (1, 2), (2, 3), (3, 4)],
    },
}
