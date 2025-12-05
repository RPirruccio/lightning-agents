"""
Database utilities - Shared functions for filesystem-based operations.
"""

from datetime import datetime, timezone
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    # Navigate from src/lightning_agents/lib/ to project root
    return Path(__file__).parent.parent.parent.parent


def get_agents_base_path() -> Path:
    """Get the path to .claude/agents/ directory."""
    return get_project_root() / ".claude" / "agents"


def get_skills_base_path() -> Path:
    """Get the path to .claude/skills/ directory."""
    return get_project_root() / ".claude" / "skills"


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_agent_definition(agent_data: dict) -> tuple[bool, str | None]:
    """
    Validate an agent definition has required fields.

    Returns:
        (is_valid, error_message)
    """
    required = {"name", "description", "system_prompt", "model"}
    missing = required - set(agent_data.keys())

    if missing:
        return False, f"Missing required fields: {missing}"

    if agent_data.get("model") not in ("haiku", "sonnet"):
        return False, f"Invalid model: {agent_data.get('model')}. Must be 'haiku' or 'sonnet'"

    if "tools" in agent_data and not isinstance(agent_data["tools"], list):
        return False, "Tools must be a list"

    return True, None


def validate_skill_definition(skill_data: dict) -> tuple[bool, str | None]:
    """
    Validate a skill definition has required fields.

    Returns:
        (is_valid, error_message)
    """
    required = {"name", "description"}
    missing = required - set(skill_data.keys())

    if missing:
        return False, f"Missing required fields: {missing}"

    return True, None
