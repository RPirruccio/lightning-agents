"""Parse SKILL.md files (YAML frontmatter + markdown body)."""

import yaml
from pathlib import Path
from typing import Any


def parse_skill_md(path: Path) -> dict[str, Any]:
    """
    Parse a SKILL.md file into a dictionary.

    Format:
    ---
    name: Skill Name
    description: One-line description
    ---

    [Skill content as markdown body]

    Returns:
        Dict with frontmatter fields plus 'content' from body
    """
    text = path.read_text()

    # Split YAML frontmatter from markdown body
    if not text.startswith('---'):
        raise ValueError(f"SKILL.md must start with YAML frontmatter: {path}")

    parts = text.split('---', 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid SKILL.md format (missing closing ---): {path}")

    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()

    # Merge frontmatter with body as content
    return {
        **frontmatter,
        'content': body,
    }
