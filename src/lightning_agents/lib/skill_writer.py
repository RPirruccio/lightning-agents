"""Write SKILL.md files (YAML frontmatter + markdown body)."""

import yaml
from pathlib import Path
from typing import Any


def write_skill_md(skill_id: str, data: dict[str, Any], base_path: Path) -> Path:
    """
    Write a skill definition to SKILL.md file.

    Creates directory structure: base_path/<skill_id>/SKILL.md

    Args:
        skill_id: The skill identifier (used as directory name)
        data: Dict with name, description, content
        base_path: Base directory (e.g., .claude/skills/)

    Returns:
        Path to created SKILL.md file
    """
    # Make a copy to avoid mutating input
    data = dict(data)

    # Separate content from frontmatter
    content = data.pop('content', '')

    # Create directory
    skill_dir = base_path / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Build YAML frontmatter (preserve key order)
    frontmatter = yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    # Build full content
    full_content = f"---\n{frontmatter}---\n\n{content}\n"

    # Write file
    skill_file = skill_dir / 'SKILL.md'
    skill_file.write_text(full_content)

    return skill_file
