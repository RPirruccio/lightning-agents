"""
Database utilities - Shared functions for CRUD operations on db/ files.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def get_db_path() -> Path:
    """Get the path to the db/ directory."""
    # Navigate from src/lightning_agents/tools/ to project root db/
    return Path(__file__).parent.parent.parent.parent / "db"


def get_agents_db_path() -> Path:
    """Get the path to db/agents.json."""
    return get_db_path() / "agents.json"


def get_tools_db_path() -> Path:
    """Get the path to db/tools.json."""
    return get_db_path() / "tools.json"


def read_json_db(path: Path) -> dict[str, Any]:
    """Read and parse a JSON database file."""
    with open(path) as f:
        return json.load(f)


def write_json_db(path: Path, data: dict[str, Any]) -> None:
    """Write data to a JSON database file, updating metadata timestamp."""
    if "metadata" in data:
        data["metadata"]["updated_at"] = get_timestamp()

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


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


def validate_tool_definition(tool_data: dict) -> tuple[bool, str | None]:
    """
    Validate a tool definition has required fields.

    Returns:
        (is_valid, error_message)
    """
    required = {"name", "description", "module", "function", "parameters"}
    missing = required - set(tool_data.keys())

    if missing:
        return False, f"Missing required fields: {missing}"

    if not isinstance(tool_data.get("parameters"), dict):
        return False, "Parameters must be a dictionary"

    return True, None
