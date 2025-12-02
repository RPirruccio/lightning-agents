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
            "Hardcoded system prompts scattered across files",
            "Tightly coupled agent definitions and execution logic",
            "No standardized way to add new agents without code changes",
            "Manual configuration duplication when agents share patterns",
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
        "title": "Runtime Context Injection",
        "bullets": [
            "Same definition, different contexts",
            "Inject parameters at instantiation time",
            "agent.prompt merges base + runtime context",
            "Enables agent reusability across use cases",
        ],
    },
    {
        "type": "diagram",
        "title": "The Architect Agent",
        "diagram_id": "architect_flow",
    },
    {
        "type": "bullets",
        "title": "Demo Flow",
        "bullets": [
            "lightning list → Show available agents",
            "lightning run lab_finder \"RAG tutorials\" → Use existing agent",
            "lightning architect \"meeting summarizer\" → Create NEW agent",
            "lightning list → New agent now available!",
            "lightning run meeting_summarizer \"...\" → Use it immediately",
        ],
    },
    {
        "type": "bullets",
        "title": "Key Hypotheses",
        "bullets": [
            "H1: Declarative > Imperative for agent configuration",
            "H2: Runtime context injection enables reusability",
            "H3: Architect agents enable organic system growth",
        ],
    },
    {
        "type": "code",
        "title": "Live Demo",
        "code": '''$ lightning list
  architect, aimug_researcher, lab_finder...

$ lightning architect "PR reviewer for security"

Created agent: security_reviewer
Saved to: agents.json

$ lightning run security_reviewer "Review auth.py"''',
    },
    {
        "type": "closing",
        "title": "Lightning Agents",
        "bullets": [
            "github.com/[your-repo]/lightning-agents",
            "Built with Claude Agent SDK",
            "Questions?",
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
