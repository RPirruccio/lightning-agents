"""
Agent Registry - Load definitions, build factories, instantiate agents.

The registry is the "factory of factories":
- Loads agent blueprints from .claude/agents/<id>/AGENT.md
- Builds factory functions for each
- Provides a unified interface for agent creation
"""

from pathlib import Path
from typing import Any, TYPE_CHECKING

from .agent_factory import AgentDefinition, AgentFactory, AgentInstance, build_factory
from .agent_parser import parse_agent_md
from .agent_writer import write_agent_md

if TYPE_CHECKING:
    from claude_agent_sdk.types import AgentDefinition as SDKAgentDefinition


def get_default_agents_path() -> Path:
    """Get the default path to .claude/agents/ directory."""
    # Navigate from src/lightning_agents/lib/ to project root
    return Path(__file__).parent.parent.parent.parent / ".claude" / "agents"


class AgentRegistry:
    """
    Central registry for all agent definitions.

    Flow: AGENT.md → Definition → Factory → Instance

    Usage:
        registry = AgentRegistry.from_filesystem()
        agent = registry.create("basic_helper", {"user_name": "Alice"})
    """

    def __init__(self):
        self._definitions: dict[str, AgentDefinition] = {}
        self._factories: dict[str, AgentFactory] = {}

    def register(self, agent_id: str, definition: AgentDefinition) -> None:
        """Register a definition and build its factory."""
        self._definitions[agent_id] = definition
        self._factories[agent_id] = build_factory(definition)

    def create(
        self,
        agent_id: str,
        runtime_opts: dict[str, Any] | None = None
    ) -> AgentInstance:
        """Create an agent instance by ID."""
        if agent_id not in self._factories:
            available = ", ".join(self._definitions.keys())
            raise KeyError(f"Agent '{agent_id}' not found. Available: {available}")

        factory = self._factories[agent_id]
        return factory(runtime_opts)

    def list_agents(self) -> list[str]:
        """Return all registered agent IDs."""
        return list(self._definitions.keys())

    def get_definition(self, agent_id: str) -> AgentDefinition:
        """Get the raw definition for an agent."""
        return self._definitions[agent_id]

    def get_configured_subagents(
        self,
        parent_agent_id: str
    ) -> dict[str, "SDKAgentDefinition"]:
        """Get only the subagents explicitly configured for an agent."""
        parent_defn = self._definitions.get(parent_agent_id)
        if not parent_defn:
            return {}

        configured_ids = parent_defn.subagents or []
        if not configured_ids:
            return {}

        return {
            agent_id: self._definitions[agent_id].to_sdk_definition()
            for agent_id in configured_ids
            if agent_id in self._definitions and agent_id != parent_agent_id
        }

    @classmethod
    def from_filesystem(cls, base_path: Path | None = None) -> "AgentRegistry":
        """Load registry from filesystem (.claude/agents/**/AGENT.md)."""
        registry = cls()
        base = base_path or get_default_agents_path()

        if not base.exists():
            return registry

        for agent_dir in sorted(base.iterdir()):
            if not agent_dir.is_dir():
                continue

            agent_file = agent_dir / "AGENT.md"
            if not agent_file.exists():
                continue

            agent_id = agent_dir.name
            data = parse_agent_md(agent_file)
            definition = AgentDefinition.from_md_dict(data)
            registry.register(agent_id, definition)

        return registry

    def save_agent(self, agent_id: str, base_path: Path | None = None) -> Path:
        """Save a single agent to filesystem as AGENT.md."""
        if agent_id not in self._definitions:
            raise KeyError(f"Agent '{agent_id}' not found")

        defn = self._definitions[agent_id]
        base = base_path or get_default_agents_path()

        data = defn.to_md_dict()
        return write_agent_md(agent_id, data, base)

    def delete_agent_file(self, agent_id: str, base_path: Path | None = None) -> None:
        """Delete an agent's directory from filesystem."""
        import shutil
        base = base_path or get_default_agents_path()
        agent_dir = base / agent_id
        if agent_dir.exists():
            shutil.rmtree(agent_dir)
