"""
Agent Factory - Builds callable factories from agent definitions.

The factory pattern enables:
1. Deferred instantiation - agents are created only when needed
2. Runtime customization - inject context at creation time
3. Separation of definition from execution
"""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class AgentDefinition:
    """Blueprint for an agent - loaded from JSON."""

    name: str
    description: str
    system_prompt: str
    model: str = "sonnet"
    tools: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentDefinition":
        return cls(
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            model=data.get("model", "sonnet"),
            tools=data.get("tools", []),
        )


@dataclass
class AgentInstance:
    """A configured agent ready to run."""

    definition: AgentDefinition
    runtime_context: dict[str, Any] = field(default_factory=dict)

    @property
    def prompt(self) -> str:
        """Build final prompt with runtime context."""
        base = self.definition.system_prompt
        if self.runtime_context:
            context_str = "\n".join(
                f"- {k}: {v}" for k, v in self.runtime_context.items()
            )
            return f"{base}\n\n## Runtime Context\n{context_str}"
        return base


# Type alias for factory functions
AgentFactory = Callable[[dict[str, Any]], AgentInstance]


def build_factory(definition: AgentDefinition) -> AgentFactory:
    """
    Build a factory function from a definition.

    The returned factory accepts runtime options and produces
    a fully configured AgentInstance.

    Args:
        definition: The agent blueprint

    Returns:
        A callable that creates AgentInstance objects
    """
    def factory(runtime_opts: dict[str, Any] | None = None) -> AgentInstance:
        return AgentInstance(
            definition=definition,
            runtime_context=runtime_opts or {},
        )

    return factory
