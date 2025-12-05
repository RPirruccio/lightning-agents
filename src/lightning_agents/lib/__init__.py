"""
Lightning Agents Library - Framework internals.

This module contains all framework code:
- Agent registry and factory
- Runner and execution
- MCP tool implementations (CRUD for agents/skills)
- Utilities and parsers
"""

# Core components
from .registry import AgentRegistry
from .runner import run_agent_by_id, run_agent_capture
from .agent_factory import AgentDefinition, AgentInstance, build_factory

# Parsers and writers
from .agent_parser import parse_agent_md
from .agent_writer import write_agent_md

# Logging
from .agent_logger import AgentLogger

# MCP config
from .mcp_config import get_mcp_servers

# Database utilities
from .db_utils import (
    get_project_root,
    get_agents_base_path,
    get_skills_base_path,
    get_timestamp,
    validate_agent_definition,
)

# CRUD tools for agents
from .db_agents import (
    db_list_agents,
    db_get_agent,
    db_create_agent,
    db_update_agent,
    db_delete_agent,
)

# CRUD tools for skills
from .db_skills import (
    db_list_skills,
    db_get_skill,
    db_create_skill,
    db_delete_skill,
)

# Sub-agent invocation
from .run_agent import run_agent

__all__ = [
    # Core
    "AgentRegistry",
    "run_agent_by_id",
    "run_agent_capture",
    "AgentDefinition",
    "AgentInstance",
    "build_factory",
    # Parsers
    "parse_agent_md",
    "write_agent_md",
    # Logging
    "AgentLogger",
    # MCP
    "get_mcp_servers",
    # Utils
    "get_project_root",
    "get_agents_base_path",
    "get_skills_base_path",
    "get_timestamp",
    "validate_agent_definition",
    # Agent CRUD
    "db_list_agents",
    "db_get_agent",
    "db_create_agent",
    "db_update_agent",
    "db_delete_agent",
    # Skill CRUD
    "db_list_skills",
    "db_get_skill",
    "db_create_skill",
    "db_delete_skill",
    # Sub-agent
    "run_agent",
]
