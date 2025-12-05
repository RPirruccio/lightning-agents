#!/usr/bin/env python3
"""
Migration script: db/agents.json → .claude/agents/<id>/AGENT.md

Converts all agents from centralized JSON to filesystem-based AGENT.md files.
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from lightning_agents.agent_writer import write_agent_md


def migrate():
    """Migrate agents from JSON to filesystem."""
    json_path = project_root / "db" / "agents.json"
    agents_dir = project_root / ".claude" / "agents"

    if not json_path.exists():
        print(f"❌ Source file not found: {json_path}")
        return False

    # Read source JSON
    with open(json_path) as f:
        data = json.load(f)

    agents = data.get("agents", {})
    print(f"📦 Found {len(agents)} agents to migrate\n")

    # Create base directory
    agents_dir.mkdir(parents=True, exist_ok=True)

    # Migrate each agent
    migrated = []
    for agent_id, agent_data in agents.items():
        # Build the data dict for AGENT.md
        md_data = {
            "name": agent_data["name"],
            "description": agent_data["description"],
            "model": agent_data.get("model", "sonnet"),
            "tools": agent_data.get("tools", []),
            "skills": agent_data.get("skills", []),
            "subagents": agent_data.get("subagents", []),
            "created_at": agent_data.get("created_at", ""),
            "updated_at": agent_data.get("updated_at", ""),
            "system_prompt": agent_data.get("system_prompt", ""),
        }

        # Write the AGENT.md file
        output_path = write_agent_md(agent_id, md_data, agents_dir)
        print(f"  ✓ {agent_id} → {output_path.relative_to(project_root)}")
        migrated.append(agent_id)

    print(f"\n✅ Migrated {len(migrated)} agents to .claude/agents/")
    return True


def verify():
    """Verify the migration by loading from filesystem."""
    from lightning_agents.registry import AgentRegistry

    registry = AgentRegistry.from_filesystem()
    agents = registry.list_agents()

    print(f"\n🔍 Verification: Loaded {len(agents)} agents from filesystem")
    for agent_id in sorted(agents):
        defn = registry.get_definition(agent_id)
        print(f"  ✓ {agent_id}: {defn.name} ({defn.model})")

    return len(agents) > 0


if __name__ == "__main__":
    print("=" * 60)
    print("Agent Migration: JSON → Filesystem")
    print("=" * 60 + "\n")

    if migrate():
        if verify():
            print("\n" + "=" * 60)
            print("Migration complete! Next steps:")
            print("  1. Run: lightning list")
            print("  2. Test: lightning run basic_helper 'Hello'")
            print("  3. Delete deprecated: rm db/agents.json db/tools.json")
            print("=" * 60)
        else:
            print("\n❌ Verification failed!")
            sys.exit(1)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
