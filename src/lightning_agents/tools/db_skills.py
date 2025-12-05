"""
Skill CRUD tools - MCP tools for managing db/skills.json.

These tools enable agents to directly persist and manage
skill definitions in the database.
"""

from claude_agent_sdk import tool

from .db_utils import (
    get_skills_db_path,
    read_json_db,
    write_json_db,
    get_timestamp,
    validate_skill_definition,
)


@tool("db_list_skills", "List all registered skills in the database", {})
async def db_list_skills(args: dict) -> dict:
    """List all skills with their basic info."""
    db = read_json_db(get_skills_db_path())
    skills = db.get("skills", {})

    result = []
    for skill_id, skill_data in skills.items():
        result.append(
            {
                "id": skill_id,
                "name": skill_data.get("name"),
                "description": skill_data.get("description"),
                "path": skill_data.get("path"),
                "version": skill_data.get("version", "N/A"),
                "source_agent": skill_data.get("source_agent", "N/A"),
            }
        )

    return {
        "content": [
            {
                "type": "text",
                "text": f"Found {len(result)} skills:\n"
                + "\n".join(f"- {s['id']}: {s['description']} (path: {s['path']})" for s in result),
            }
        ]
    }


@tool("db_get_skill", "Get full details of a skill by ID", {"skill_id": str})
async def db_get_skill(args: dict) -> dict:
    """Get complete skill definition."""
    skill_id = args["skill_id"]
    db = read_json_db(get_skills_db_path())
    skills = db.get("skills", {})

    if skill_id not in skills:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Skill '{skill_id}' not found. Available: {', '.join(skills.keys())}",
                }
            ],
            "isError": True,
        }

    skill = skills[skill_id]
    import json

    return {
        "content": [{"type": "text", "text": f"Skill: {skill_id}\n{json.dumps(skill, indent=2)}"}]
    }


@tool(
    "db_create_skill",
    "Create a new skill in the database",
    {
        "skill_id": str,
        "name": str,
        "description": str,
        "path": str,
        "version": str,
        "source_agent": str,
    },
)
async def db_create_skill(args: dict) -> dict:
    """Create a new skill definition."""
    skill_id = args["skill_id"]

    # Build skill data from args - only required fields are mandatory
    skill_data = {
        "name": args["name"],
        "description": args["description"],
        "path": args["path"],
    }

    # Add optional fields if provided
    if "version" in args and args["version"]:
        skill_data["version"] = args["version"]
    if "source_agent" in args and args["source_agent"]:
        skill_data["source_agent"] = args["source_agent"]

    # Validate
    is_valid, error = validate_skill_definition(skill_data)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid skill definition: {error}"}],
            "isError": True,
        }

    # Read current DB
    db_path = get_skills_db_path()
    db = read_json_db(db_path)
    skills = db.get("skills", {})

    # Check if exists
    if skill_id in skills:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Skill '{skill_id}' already exists. Use db_update_skill to modify.",
                }
            ],
            "isError": True,
        }

    # Add timestamps and save
    skill_data["created_at"] = get_timestamp()
    skill_data["updated_at"] = get_timestamp()
    skills[skill_id] = skill_data
    db["skills"] = skills

    write_json_db(db_path, db)

    return {
        "content": [
            {
                "type": "text",
                "text": f"Created skill '{skill_id}' successfully!\n\nName: {skill_data['name']}\nPath: {skill_data['path']}\nDescription: {skill_data['description']}",
            }
        ]
    }


@tool(
    "db_update_skill",
    "Update an existing skill in the database",
    {
        "skill_id": str,
        "name": str,
        "description": str,
        "path": str,
        "version": str,
        "source_agent": str,
    },
)
async def db_update_skill(args: dict) -> dict:
    """Update an existing skill definition."""
    skill_id = args["skill_id"]

    # Read current DB
    db_path = get_skills_db_path()
    db = read_json_db(db_path)
    skills = db.get("skills", {})

    # Check exists
    if skill_id not in skills:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Skill '{skill_id}' not found. Use db_create_skill to create.",
                }
            ],
            "isError": True,
        }

    # Get existing and update
    existing = skills[skill_id]

    # Update only provided fields
    if "name" in args and args["name"]:
        existing["name"] = args["name"]
    if "description" in args and args["description"]:
        existing["description"] = args["description"]
    if "path" in args and args["path"]:
        existing["path"] = args["path"]
    if "version" in args and args["version"]:
        existing["version"] = args["version"]
    if "source_agent" in args and args["source_agent"]:
        existing["source_agent"] = args["source_agent"]

    # Validate
    is_valid, error = validate_skill_definition(existing)
    if not is_valid:
        return {
            "content": [{"type": "text", "text": f"Invalid skill definition: {error}"}],
            "isError": True,
        }

    # Update timestamp and save
    existing["updated_at"] = get_timestamp()
    skills[skill_id] = existing
    db["skills"] = skills

    write_json_db(db_path, db)

    return {"content": [{"type": "text", "text": f"Updated skill '{skill_id}' successfully!"}]}


@tool("db_delete_skill", "Delete a skill from the database", {"skill_id": str})
async def db_delete_skill(args: dict) -> dict:
    """Delete a skill definition."""
    skill_id = args["skill_id"]

    # Read current DB
    db_path = get_skills_db_path()
    db = read_json_db(db_path)
    skills = db.get("skills", {})

    # Check exists
    if skill_id not in skills:
        return {
            "content": [{"type": "text", "text": f"Skill '{skill_id}' not found."}],
            "isError": True,
        }

    # Delete and save
    deleted = skills.pop(skill_id)
    db["skills"] = skills

    write_json_db(db_path, db)

    return {
        "content": [
            {
                "type": "text",
                "text": f"Deleted skill '{skill_id}' ({deleted['name']}) successfully!",
            }
        ]
    }
