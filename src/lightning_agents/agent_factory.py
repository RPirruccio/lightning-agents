"""
Agent Factory - Builds callable factories from agent definitions.

The factory pattern enables:
1. Deferred instantiation - agents are created only when needed
2. Runtime customization - inject context at creation time
3. Separation of definition from execution
"""

from dataclasses import dataclass, field
from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from claude_agent_sdk.types import AgentDefinition as SDKAgentDefinition


@dataclass
class AgentDefinition:
    """Blueprint for an agent - loaded from AGENT.md files."""

    name: str
    description: str
    system_prompt: str
    model: str = "sonnet"
    tools: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    subagents: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentDefinition":
        """Load from legacy JSON format."""
        return cls(
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            model=data.get("model", "sonnet"),
            tools=data.get("tools", []),
            skills=data.get("skills", []),
            subagents=data.get("subagents", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    @classmethod
    def from_md_dict(cls, data: dict[str, Any]) -> "AgentDefinition":
        """Load from parsed AGENT.md format."""
        return cls(
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            model=data.get("model", "sonnet"),
            tools=data.get("tools", []),
            skills=data.get("skills", []),
            subagents=data.get("subagents", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    def to_md_dict(self) -> dict[str, Any]:
        """Convert to AGENT.md format dict."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "tools": self.tools,
            "skills": self.skills,
            "subagents": self.subagents,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "system_prompt": self.system_prompt,
        }

    def to_sdk_definition(self) -> "SDKAgentDefinition":
        """Convert to Claude Agent SDK AgentDefinition format."""
        from claude_agent_sdk.types import AgentDefinition as SDKAgentDef
        return SDKAgentDef(
            name=self.name,
            description=self.description,
            model=self.model,
            allowed_tools=self.tools if self.tools else None,
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
