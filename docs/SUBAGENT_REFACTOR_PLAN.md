# Subagent Refactoring Plan: MCP Tools to Native SDK Subagents

## Executive Summary

This document details the migration of Lightning Agents from MCP tool-based sub-agent execution (`mcp__custom-tools__run_agent`) to the Claude Agent SDK's native `agents` parameter in `ClaudeAgentOptions`. This migration enables:

1. **Autonomous subagent invocation** - Claude decides when to invoke subagents based on their descriptions
2. **SDK-managed parallelism** - The SDK handles concurrent subagent execution
3. **Simplified architecture** - Removes custom MCP tool layer for sub-agent invocation
4. **Better observability** - Native `SubagentStop` hooks for logging

---

## Current State Analysis

### Architecture Overview

```
                    +------------------+
                    |   CLI (cli.py)   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | AgentRegistry    |
                    | (registry.py)    |
                    +--------+---------+
                             |
            +----------------+----------------+
            |                                 |
            v                                 v
    +---------------+                +------------------+
    | AgentFactory  |                | run_agent_by_id  |
    | (agent_       |                | (runner.py)      |
    | factory.py)   |                +--------+---------+
    +-------+-------+                         |
            |                                 v
            v                         +------------------+
    +---------------+                 | ClaudeSDKClient  |
    | AgentInstance |                 | (ClaudeAgent     |
    +---------------+                 |  Options)        |
                                      +--------+---------+
                                               |
                    +--------------------------+
                    |
                    v
            +------------------+
            | MCP Servers      |
            | - searxng        |
            | - custom-tools   |<---- Contains run_agent tool
            +------------------+
```

### Current Sub-Agent Flow

1. **Parent agent** uses `mcp__custom-tools__run_agent` MCP tool
2. **run_agent tool** (`/src/lightning_agents/tools/run_agent.py`):
   - Loads `AgentRegistry` from `db/agents.json`
   - Creates `AgentInstance` for target agent
   - Calls `run_agent_capture()` in `runner.py`
3. **run_agent_capture()** creates a **new** `ClaudeSDKClient` session
4. Sub-agent runs **sequentially** (blocks parent until complete)
5. Result returned as MCP tool response

### Current Limitations

1. **Sequential execution** - Sub-agents run one at a time
2. **Manual orchestration** - Parent agent must explicitly call `run_agent` tool
3. **Separate sessions** - Each sub-agent creates new `ClaudeSDKClient` session
4. **No SDK parallelism** - Cannot leverage SDK's built-in concurrent execution
5. **Complex logging** - Custom logging in `run_agent_capture()` separate from main flow

---

## Target State Description

### Native SDK Subagent Architecture

```
                    +------------------+
                    |   CLI (cli.py)   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | AgentRegistry    |
                    | (registry.py)    |
                    +--------+---------+
                             |
          +------------------+------------------+
          |                                     |
          v                                     v
  +---------------+                    +------------------+
  | AgentFactory  |                    | run_agent_by_id  |
  | (agent_       |                    | (runner.py)      |
  | factory.py)   |                    +--------+---------+
  +-------+-------+                             |
          |                                     |
          v                                     v
  +---------------+                    +------------------+
  | AgentInstance |                    | ClaudeAgentOptions|
  +---------------+                    |   .agents = {    |
                                       |     "slides_checker": AgentDefinition(...),
                                       |     "tool_implementer": AgentDefinition(...),
                                       |   }              |
                                       +--------+---------+
                                                |
                                                v
                                       +------------------+
                                       | ClaudeSDKClient  |
                                       | (Autonomous      |
                                       |  Subagent        |
                                       |  Invocation)     |
                                       +--------+---------+
                                                |
                                     +----------+----------+
                                     |          |          |
                                     v          v          v
                               [Subagent] [Subagent] [Subagent]
                               (Parallel execution managed by SDK)
```

### Benefits of Native Subagents

1. **Autonomous invocation** - Claude decides based on agent descriptions
2. **SDK-managed parallelism** - Concurrent execution handled by SDK
3. **Single session** - All subagents run within parent's session context
4. **Built-in hooks** - `SubagentStop` for observability
5. **Simplified code** - Remove `run_agent` tool and `run_agent_capture()`

---

## Step-by-Step Migration Tasks

### Phase 1: Registry and Factory Changes

#### Task 1.1: Create SDK AgentDefinition Converter

**File**: `/src/lightning_agents/agent_factory.py`

```python
from claude_agent_sdk.types import AgentDefinition as SDKAgentDefinition

@dataclass
class AgentDefinition:
    # ... existing fields ...

    def to_sdk_definition(self) -> SDKAgentDefinition:
        """Convert to Claude Agent SDK AgentDefinition format."""
        filtered_tools = [
            t for t in self.tools
            if t != "mcp__custom-tools__run_agent"
        ]

        return SDKAgentDefinition(
            description=self.description,
            prompt=self.system_prompt,
            tools=filtered_tools if filtered_tools else None,
            model=self._normalize_model()
        )

    def _normalize_model(self) -> str | None:
        if self.model in ("sonnet", "opus", "haiku"):
            return self.model
        return "inherit"
```

#### Task 1.2: Add Subagent Extraction to Registry

**File**: `/src/lightning_agents/registry.py`

```python
def get_available_subagents(self, parent_agent_id: str) -> dict[str, SDKAgentDefinition]:
    """Get subagents available to a specific parent agent."""
    return {
        agent_id: defn.to_sdk_definition()
        for agent_id, defn in self._definitions.items()
        if agent_id != parent_agent_id
    }
```

### Phase 2: Runner Changes

#### Task 2.1: Add Subagent Support to run_agent()

**File**: `/src/lightning_agents/runner.py`

```python
async def run_agent(
    instance: AgentInstance,
    prompt: str,
    stream: bool = True,
    verbose: bool = True,
    subagents: dict[str, SDKAgentDefinition] | None = None,
) -> str:
    mcp_servers = get_mcp_servers(instance.definition.tools)

    hooks = None
    if subagents and verbose:
        hooks = {
            "SubagentStop": [HookMatcher(hooks=[_create_subagent_logger(instance)])]
        }

    options = ClaudeAgentOptions(
        system_prompt=instance.prompt,
        allowed_tools=instance.definition.tools or [],
        mcp_servers=mcp_servers if mcp_servers else None,
        agents=subagents,
        hooks=hooks,
    )
    # ... rest unchanged ...
```

### Phase 3: Logging Strategy with SubagentStop Hooks

**File**: `/src/lightning_agents/agent_logger.py` (new)

```python
def create_subagent_stop_logger(parent_agent_id: str, log_dir: Path | None = None):
    """Create a SubagentStop hook that logs subagent execution."""

    async def subagent_stop_hook(input, tool_use_id, context):
        session_id = input.get("session_id", "unknown")
        timestamp = datetime.now().isoformat()
        log_file = log_dir / f"{parent_agent_id}_subagent_{session_id[:8]}.log"

        with open(log_file, "a") as f:
            f.write(f"\n[{timestamp}] SubagentStop\n")
            f.write(f"  Session: {session_id}\n")

        print(f"  [SubagentStop] Session {session_id[:8]}... completed")
        return {"continue_": True}

    return subagent_stop_hook
```

### Phase 4: Agent Definition Cleanup

Remove `mcp__custom-tools__run_agent` from all agent tool lists - SDK handles orchestration automatically.

Update system prompts to reference subagents naturally instead of explicit tool calls.

---

## Implementation Tasks (Clean Rip-and-Replace)

### Step 1: Factory & Registry
- [ ] Add `to_sdk_definition()` to `agent_factory.py`
- [ ] Add `get_available_subagents()` to `registry.py`

### Step 2: Runner Integration
- [ ] Update `run_agent()` with `subagents` parameter
- [ ] Update `run_agent_by_id()` to wire subagents
- [ ] Add SubagentStop hook for logging

### Step 3: Cleanup
- [ ] Remove `run_agent` tool from `tools/__init__.py`
- [ ] Remove `run_agent_capture()` from `runner.py`
- [ ] Remove `mcp__custom-tools__run_agent` from all agent definitions
- [ ] Update agent system prompts

### Step 4: Testing
- [ ] Unit tests for conversion
- [ ] Integration tests for subagent invocation
- [ ] E2E test with slides_checker orchestration

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| SDK behavior differences | Test thoroughly before deploying |
| Circular dependencies | SDK handles internally; exclude parent from subagents |
| Tool access in subagents | Explicitly pass tools in AgentDefinition |
| Logging gaps | Use SubagentStop hook + transcript files |

---

## Critical Files

- `/src/lightning_agents/agent_factory.py` - Add `to_sdk_definition()`
- `/src/lightning_agents/registry.py` - Add `get_available_subagents()`
- `/src/lightning_agents/runner.py` - Wire subagents into ClaudeAgentOptions
- `/src/lightning_agents/agent_logger.py` - SubagentStop hook (new file)
- `/src/lightning_agents/tools/run_agent.py` - Deprecation warning

---

*Generated by Plan agent - 2025-12-03*
