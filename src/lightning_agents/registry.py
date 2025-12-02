"""
Agent Registry - Load definitions, build factories, instantiate agents.

The registry is the "factory of factories":
- Loads agent blueprints from JSON (default: db/agents.json)
- Builds factory functions for each
- Provides a unified interface for agent creation
"""

import json
from pathlib import Path
from typing import Any

from .agent_factory import AgentDefinition, AgentFactory, AgentInstance, build_factory


def get_default_db_path() -> Path:
    """Get the default path to db/agents.json."""
    # Navigate from src/lightning_agents/ to project root db/
    return Path(__file__).parent.parent.parent / "db" / "agents.json"


class AgentRegistry:
    """
    Central registry for all agent definitions.

    Flow: JSON → Definition → Factory → Instance

    Usage:
        registry = AgentRegistry.from_json("agents.json")
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
        """
        Create an agent instance by ID.

        Args:
            agent_id: The agent identifier from JSON
            runtime_opts: Runtime context to inject

        Returns:
            A configured AgentInstance ready to execute

        Raises:
            KeyError: If agent_id not found
        """
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

    @classmethod
    def from_json(cls, path: str | Path) -> "AgentRegistry":
        """
        Load registry from a JSON file.

        Expected format:
        {
            "agents": {
                "agent_id": { ...definition... }
            }
        }
        """
        registry = cls()

        with open(path) as f:
            data = json.load(f)

        for agent_id, agent_data in data.get("agents", {}).items():
            definition = AgentDefinition.from_dict(agent_data)
            registry.register(agent_id, definition)

        return registry

    def save_json(self, path: str | Path) -> None:
        """Save current registry state to JSON."""
        data = {
            "agents": {
                agent_id: {
                    "name": defn.name,
                    "description": defn.description,
                    "system_prompt": defn.system_prompt,
                    "model": defn.model,
                    "tools": defn.tools,
                }
                for agent_id, defn in self._definitions.items()
            }
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)
