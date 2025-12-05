"""Parse AGENT.md files (YAML frontmatter + markdown body)."""

import yaml
from pathlib import Path
from typing import Any


def parse_agent_md(path: Path) -> dict[str, Any]:
    """
    Parse an AGENT.md file into a dictionary.

    Format:
    ---
    name: Agent Name
    description: One-line description
    model: haiku|sonnet
    tools: [...]
    skills: [...]
    subagents: [...]
    created_at: ISO timestamp
    updated_at: ISO timestamp
    ---

    [System prompt as markdown body]

    Returns:
        Dict with all frontmatter fields plus 'system_prompt' from body
    """
    content = path.read_text()

    # Split YAML frontmatter from markdown body
    if not content.startswith('---'):
        raise ValueError(f"AGENT.md must start with YAML frontmatter: {path}")

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid AGENT.md format (missing closing ---): {path}")

    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()

    # Merge frontmatter with body as system_prompt
    return {
        **frontmatter,
        'system_prompt': body,
    }
