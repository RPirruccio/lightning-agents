"""Write AGENT.md files (YAML frontmatter + markdown body)."""

import yaml
from pathlib import Path
from typing import Any


def write_agent_md(agent_id: str, data: dict[str, Any], base_path: Path) -> Path:
    """
    Write an agent definition to AGENT.md file.

    Creates directory structure: base_path/<agent_id>/AGENT.md

    Args:
        agent_id: The agent identifier (used as directory name)
        data: Dict with name, description, model, tools, skills, subagents,
              system_prompt, created_at, updated_at
        base_path: Base directory (e.g., .claude/agents/)

    Returns:
        Path to created AGENT.md file
    """
    # Make a copy to avoid mutating input
    data = dict(data)

    # Separate system_prompt from frontmatter
    system_prompt = data.pop('system_prompt', '')

    # Create directory
    agent_dir = base_path / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Build YAML frontmatter (preserve key order)
    frontmatter = yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    # Build full content
    content = f"---\n{frontmatter}---\n\n{system_prompt}\n"

    # Write file
    agent_file = agent_dir / 'AGENT.md'
    agent_file.write_text(content)

    return agent_file
