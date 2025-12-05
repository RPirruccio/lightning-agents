"""
Skill CRUD tools - MCP tools for managing .claude/skills/<id>/SKILL.md files.

These tools enable agents to directly persist and manage
skill definitions on the filesystem.
"""

import json as json_module
import shutil

from claude_agent_sdk import tool

from .db_utils import get_skills_base_path, validate_skill_definition
from .skill_parser import parse_skill_md
from .skill_writer import write_skill_md


def _list_skill_ids() -> list[str]:
    """Get list of all skill IDs from filesystem."""
    base = get_skills_base_path()
    if not base.exists():
        return []
    return sorted([
        d.name for d in base.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    ])


def _load_skill(skill_id: str) -> dict | None:
    """Load skill data from SKILL.md file."""
    base = get_skills_base_path()
    skill_file = base / skill_id / "SKILL.md"
    if not skill_file.exists():
        return None
    return parse_skill_md(skill_file)


@tool("db_list_skills", "List all registered skills", {})
async def db_list_skills(_args: dict) -> dict:
    """List all skills with their basic info."""
    result = []

    for skill_id in _list_skill_ids():
        data = _load_skill(skill_id)
        if data:
            result.append({
                "id": skill_id,
                "name": data.get("name"),
                "description": data.get("description"),
            })

    return {
        "content": [{
            "type": "text",
            "text": f"Found {len(result)} skills:\n" + "\n".join(
                f"- {s['id']}: {s['description']}"
                for s in result
            )
        }]
    }


@tool("db_get_skill", "Get full details of a skill by ID", {"skill_id": str})
async def db_get_skill(args: dict) -> dict:
    """Get complete skill definition."""
    skill_id = args["skill_id"]
    data = _load_skill(skill_id)

    if not data:
        available = _list_skill_ids()
        return {
            "content": [{
                "type": "text",
                "text": f"Skill '{skill_id}' not found. Available: {', '.join(available)}"
            }],
            "isError": True
        }

    return {
        "content": [{
            "type": "text",
            "text": f"Skill: {skill_id}\n{json_module.dumps(data, indent=2)}"
        }]
    }


@tool(
    "db_create_skill",
    "Create a new skill definition",
    {
        "skill_id": str,
        "name": str,
        "description": str,
        "content": str,
    }
)
async def db_create_skill(args: dict) -> dict:
    """Create a new skill definition as SKILL.md file."""
    skill_id = args["skill_id"]

    # Build skill data
    skill_data = {
        "name": args["name"],
        "description": args["description"],
        "content": args.get("content", ""),
    }

    # Validate
    is_valid, error = validate_skill_definition(skill_data)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid skill definition: {error}"}],
            "isError": True
        }

    # Check if exists
    if _load_skill(skill_id):
        return {
            "content": [{"type": "text", "text": f"Skill '{skill_id}' already exists."}],
            "isError": True
        }

    # Write to filesystem
    base = get_skills_base_path()
    write_skill_md(skill_id, skill_data, base)

    return {
        "content": [{
            "type": "text",
            "text": f"Created skill '{skill_id}' successfully!\n\nName: {skill_data['name']}\nDescription: {skill_data['description']}"
        }]
    }


@tool("db_delete_skill", "Delete a skill definition", {"skill_id": str})
async def db_delete_skill(args: dict) -> dict:
    """Delete a skill's directory from filesystem."""
    skill_id = args["skill_id"]

    # Check exists
    data = _load_skill(skill_id)
    if not data:
        return {
            "content": [{"type": "text", "text": f"Skill '{skill_id}' not found."}],
            "isError": True
        }

    # Delete directory
    base = get_skills_base_path()
    skill_dir = base / skill_id
    if skill_dir.exists():
        shutil.rmtree(skill_dir)

    return {
        "content": [{
            "type": "text",
            "text": f"Deleted skill '{skill_id}' ({data['name']}) successfully!"
        }]
    }
