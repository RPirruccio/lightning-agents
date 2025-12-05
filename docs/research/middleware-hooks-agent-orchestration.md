# Middleware & Hooks for Scalable Agent Orchestration

**Research Report for Lightning Agents**
*Generated: 2025-12-04*

---

## Executive Summary

This report explores the **middleware pattern** for AI agent orchestration - specifically how hooks and policy enforcement layers can solve the scalability problem when managing large numbers of subagents. The key insight: **you don't dump 100 agent descriptions into context**. Instead, you use middleware to intercept, route, validate, and control agent execution at runtime.

Two primary implementations are examined:
1. **LangGraph** - Auth/middleware pattern for behavior control and policy enforcement
2. **Claude Agent SDK** - Hooks system (PreToolUse, PostToolUse, SubagentStop, etc.)

---

## The Scalability Problem

When building multi-agent systems, a naive approach passes all available subagent definitions into context. This doesn't scale:

| Agents | Context Cost | Issues |
|--------|--------------|--------|
| 10 | ~2K tokens | Manageable |
| 100 | ~20K tokens | Context bloat |
| 1,000 | ~200K tokens | Impractical |
| 10,000+ | N/A | Impossible |

**The middleware answer**: Don't load all agents into context. Instead, intercept execution at runtime and dynamically route/validate/control.

---

## LangGraph's Middleware Pattern (LangChain 1.0 - September 2025)

LangGraph 1.0 introduced a **true middleware abstraction** for agent behavior control. This is NOT about authentication - it's about **context engineering**: controlling what goes into and comes out of the model.

### The Problem Middleware Solves

From the LangChain blog (Sept 2025):

> "While it is simple to get a basic agent abstraction up and running, it is hard to make this abstraction flexible enough to bring to production. The answer is context engineering. The context that goes into the model determines what comes out of it."

### Middleware Hooks

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

@wrap_model_call
def my_middleware(request: ModelRequest, handler) -> ModelResponse:
    # BEFORE model call - can modify request
    modified_request = request.override(
        messages=summarize_if_too_long(request.messages),
        tools=filter_dangerous_tools(request.tools)
    )

    # Call the model
    response = handler(modified_request)

    # AFTER model call - can modify response or block
    if contains_unsafe_content(response):
        return block_response(response)

    return response

agent = create_agent(
    model="gpt-4o",
    tools=tools,
    middleware=[my_middleware]
)
```

### Three Middleware Entry Points

| Entry Point | When | Use Case |
|-------------|------|----------|
| `before_model` | Before model calls | Summarize messages, inject context, update state |
| `after_model` | After model calls | Guardrails, human-in-the-loop, validation |
| `modify_model_request` | Before model calls | Modify tools, prompt, messages, model settings |

### Built-in Middleware (LangChain 1.0)

1. **Human-in-the-loop**: Uses `after_model` to pause for human approval of tool calls
2. **Summarization**: Uses `before_model` to summarize long conversations
3. **Anthropic Prompt Caching**: Uses `modify_model_request` to add cache tags

### Example: Guardrails via `after_model`

```python
from langchain.agents.middleware import Middleware

class GuardrailMiddleware(Middleware):
    def after_model(self, state, response):
        """Run after model call - can block or modify."""
        for tool_call in response.tool_calls:
            if tool_call.name == "Bash":
                if "rm -rf" in tool_call.args.get("command", ""):
                    # Block dangerous command
                    return {"goto": "human_review"}
        return None  # Continue normally
```

### Example: Context Engineering via `before_model`

```python
class SummarizationMiddleware(Middleware):
    def before_model(self, state):
        """Run before model call - can modify state."""
        messages = state["messages"]
        if len(messages) > 50:
            # Summarize old messages to control context
            summary = self.summarize(messages[:-10])
            state["messages"] = [summary] + messages[-10:]
        return state
```

### Human-in-the-Loop with `interrupt()`

```python
from langgraph.types import interrupt

def human_approval_node(state):
    """Pause for human approval before dangerous actions."""
    tool_calls = state["pending_tool_calls"]

    for call in tool_calls:
        if call.name in ["Write", "Bash", "Edit"]:
            # Pause execution, wait for human
            human_response = interrupt({
                "question": f"Approve {call.name}?",
                "tool_call": call
            })
            if not human_response["approved"]:
                return {"goto": "reject_action"}

    return {"goto": "execute_tools"}
```

### `Command` for Dynamic Control Flow

```python
from langgraph.types import Command

def supervisor_agent(state):
    """Route to specialist agents based on task."""
    if needs_sql_expert(state):
        return Command(
            goto="sql_agent",
            update={"task": state["current_task"]}
        )
    elif needs_code_review(state):
        return Command(goto="code_reviewer")
```

---

## Claude Agent SDK Hooks System

The Claude Agent SDK implements hooks as the middleware layer for behavior control and policy enforcement around **tool execution** (vs LangGraph which hooks around model calls).

### Hook Events as Interception Points

| Hook Event | When Fired | Middleware Use Case |
|------------|------------|---------------------|
| `PreToolUse` | Before tool executes | Validate inputs, block dangerous ops, modify params |
| `PostToolUse` | After tool completes | Add context to conversation, validate results |
| `PermissionRequest` | Tool needs approval | Auto-approve/deny based on policy |
| `Stop` | Agent tries to finish | Force continuation, validate completion |
| `SubagentStop` | Subagent completes | Validate results, log metrics, force continuation |
| `UserPromptSubmit` | User sends prompt | Add metadata, validate input |
| `SessionStart` | Session begins | Inject context, set behavior mode |
| `SessionEnd` | Session terminates | Cleanup, final logging |

### PreToolUse: Block, Allow, Modify, or Give Feedback

From official Anthropic docs - `PreToolUse` can return:

```python
# Hook output options for PreToolUse:
{
    # Decision control
    "permissionDecision": "allow" | "deny" | "ask",

    # Modify tool inputs before execution
    "updatedInput": {"command": "safe-command"},

    # Give feedback to Claude (shown as reason for deny)
    "reason": "This command is dangerous because...",

    # Show warning to user
    "systemMessage": "Warning: potentially risky operation",

    # Block and stop entirely (vs deny which just blocks this call)
    "decision": "block"
}
```

### Example: Security Policy Enforcement

```python
# .claude/hooks/security_check.py
import json
import sys

# Read hook input from stdin
input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name")
tool_input = input_data.get("tool_input", {})

# Policy: Block dangerous bash commands
if tool_name == "Bash":
    command = tool_input.get("command", "")
    dangerous_patterns = ["rm -rf", "sudo", "> /dev/", "mkfs"]

    for pattern in dangerous_patterns:
        if pattern in command:
            # Return JSON to deny with feedback to Claude
            print(json.dumps({
                "permissionDecision": "deny",
                "reason": f"Command contains dangerous pattern: {pattern}",
                "systemMessage": "Blocked by security policy"
            }))
            sys.exit(0)

# Allow by default
print(json.dumps({"permissionDecision": "allow"}))
```

### Stop/SubagentStop: Force Continuation

The **killer feature** for quality loops - prevent agent from stopping prematurely:

```python
# Exit code 2 = block stop, force continuation
# This is how you implement "keep going until actually done"

import json
import sys

input_data = json.load(sys.stdin)

# Check if task is actually complete
if not all_tests_pass():
    print(json.dumps({
        "decision": "block",
        "reason": "Tests are still failing. Please fix them before stopping."
    }))
    sys.exit(2)  # Exit code 2 = block + continue

# Allow stop
sys.exit(0)
```

### Prompt-Based Hooks (LLM-Powered Middleware)

Claude Code supports **prompt-based hooks** - use an LLM to make policy decisions:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude should stop. Context: $ARGUMENTS\n\nCheck if:\n1. All tasks are complete\n2. Tests pass\n3. No errors remain\n\nRespond: {\"decision\": \"approve\" or \"block\", \"reason\": \"explanation\"}"
          }
        ]
      }
    ]
  }
}
```

This lets you make **context-aware decisions** without writing code.

### Hook Configuration in settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/security_check.py"
          }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Did the subagent complete its task? $ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

### Native SDK Subagents via `agents` Parameter

```python
from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    agents={
        "sql_expert": AgentDefinition(
            description="Handles SQL queries and database operations",
            prompt="You are a SQL expert...",
            tools=["Read", "Bash"],
            model="sonnet"
        ),
        "code_reviewer": AgentDefinition(
            description="Reviews code for bugs and security issues",
            prompt="You are a code reviewer...",
            tools=["Read", "Grep"],
            model="haiku"
        )
    },
    hooks={
        "SubagentStop": [HookMatcher(hooks=[subagent_validator])]
    }
)
```

Claude autonomously invokes subagents based on their **descriptions** - no explicit tool call needed. Hooks validate their work.

---

## Governance-as-a-Service (GaaS) Pattern

A recent research paper (arXiv:2508.18765) introduces **Governance-as-a-Service**:

> "A modular, policy-driven enforcement layer that regulates agent outputs at runtime without altering model internals or requiring agent cooperation."

### Key Concepts

| Component | Function |
|-----------|----------|
| Declarative Rules | Define policies as code, not model prompts |
| Trust Factor | Score agents based on compliance history |
| Graduated Enforcement | Warn → Limit → Block escalation |
| Runtime Interception | Evaluate ALL outputs before execution |

### Trust Factor Mechanism

```
Trust Score = f(compliance_history, violation_severity, time_decay)

High Trust (0.8-1.0): Full autonomy
Medium Trust (0.5-0.8): Enhanced monitoring
Low Trust (0.2-0.5): Human approval required
Blocked (<0.2): Agent quarantined
```

### Why This Matters for Lightning Agents

GaaS provides a model for how to:
1. **Decouple governance from agent internals**
2. **Scale policy enforcement across many agents**
3. **Maintain observability and auditability**
4. **Handle adversarial or misbehaving agents**

---

## Policy-as-Code for Agent Orchestration

From industry research, the emerging pattern is **Policy-as-Code**:

```yaml
# Example policy definition
policies:
  - name: "block_destructive_commands"
    trigger: PreToolUse
    tool: Bash
    condition: |
      "rm -rf" in args.command or
      "DROP TABLE" in args.command
    action: block
    message: "Destructive command blocked by policy"

  - name: "require_approval_for_writes"
    trigger: PreToolUse
    tool: Write
    condition: args.path.startswith("/src/")
    action: require_approval
    timeout: 300
```

### Implementation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    POLICY LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Policy Store │  │ Rule Engine  │  │ Trust Scores │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                  MIDDLEWARE LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PreToolUse   │  │ PostToolUse  │  │ SubagentStop │  │
│  │   Hooks      │  │   Hooks      │  │   Hooks      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                   AGENT LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Agent 1    │  │   Agent 2    │  │   Agent N    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Recommendations for Lightning Agents

### Phase 1: Implement SDK Hooks

Update `runner.py` to support hooks:

```python
async def run_agent(
    instance: AgentInstance,
    prompt: str,
    hooks: dict[str, list[HookMatcher]] | None = None,
    subagents: dict[str, AgentDefinition] | None = None,
) -> str:
    options = ClaudeAgentOptions(
        system_prompt=instance.prompt,
        allowed_tools=instance.definition.tools or [],
        mcp_servers=get_mcp_servers(instance.definition.tools),
        agents=subagents,
        hooks=hooks,
    )
```

### Phase 2: Add SubagentStop Logging

Create `src/lightning_agents/agent_logger.py`:

```python
from datetime import datetime
from pathlib import Path

def create_subagent_stop_hook(parent_id: str, log_dir: Path | None = None):
    """Create a SubagentStop hook for observability."""

    async def hook(input, tool_use_id, context):
        session_id = input.get("session_id", "unknown")
        timestamp = datetime.now().isoformat()

        if log_dir:
            log_file = log_dir / f"{parent_id}_subagents.log"
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] SubagentStop: session={session_id[:8]}\n")

        print(f"  [SubagentStop] {parent_id} → session {session_id[:8]} completed")
        return {"continue_": True}

    return hook
```

### Phase 3: Policy Enforcement Layer

Create policy-based hooks that can:
1. Block dangerous operations
2. Require approval for sensitive actions
3. Log all agent decisions for audit
4. Track trust scores per agent

### Phase 4: Dynamic Agent Selection (Future)

Instead of loading all agents, use retrieval:

```python
def get_relevant_subagents(task: str, top_k: int = 5) -> dict[str, AgentDefinition]:
    """Retrieve most relevant agents for a task using embeddings."""
    all_agents = registry.list_all()

    # Embed task and agent descriptions
    task_embedding = embed(task)
    agent_embeddings = {
        agent_id: embed(defn.description)
        for agent_id, defn in all_agents.items()
    }

    # Find top-k most similar
    scores = {
        agent_id: cosine_similarity(task_embedding, emb)
        for agent_id, emb in agent_embeddings.items()
    }

    top_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    return {
        agent_id: all_agents[agent_id].to_sdk_definition()
        for agent_id, _ in top_agents
    }
```

---

## LangGraph vs Claude SDK: Middleware Comparison

| Aspect | LangGraph Middleware | Claude SDK Hooks |
|--------|---------------------|------------------|
| **Hooks around** | Model calls | Tool execution |
| **Entry points** | `before_model`, `after_model`, `modify_model_request` | `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop` |
| **Context engineering** | Modify messages, tools, prompt before model | Modify tool inputs, add context after tools |
| **Guardrails** | `after_model` blocks unsafe responses | `PreToolUse` blocks unsafe tool calls |
| **Human-in-the-loop** | `interrupt()` pauses for approval | `PermissionRequest` hook for approval |
| **Force continuation** | Return `{"goto": "retry"}` | Exit code 2 on `Stop`/`SubagentStop` |
| **LLM-powered decisions** | Not built-in (implement yourself) | `type: "prompt"` hooks use Haiku |
| **Configuration** | Python code in middleware classes | JSON in settings.json + scripts |

### When to Use Which

**LangGraph Middleware** is better for:
- Context engineering (message summarization, prompt modification)
- Dynamic model/tool selection per request
- Complex state management across the graph

**Claude SDK Hooks** are better for:
- Policy enforcement on specific tools
- Quality gates (prevent premature stopping)
- Security guardrails on dangerous operations
- Observability/logging of tool execution

---

## Key Takeaways

1. **Middleware intercepts execution** - Don't dump agent descriptions into context; intercept at runtime to enforce policy and guide behavior

2. **Two interception points**:
   - LangGraph: hooks around **model calls** (`before_model`, `after_model`)
   - Claude SDK: hooks around **tool execution** (`PreToolUse`, `PostToolUse`, `Stop`)

3. **Force continuation is the killer feature** - `SubagentStop` with exit code 2 prevents agents from stopping prematurely. This is how you build quality loops.

4. **Prompt-based hooks** - Claude SDK supports LLM-powered middleware decisions without writing code

5. **Policy-as-Code** - Define rules declaratively in JSON, enforce at runtime

6. **Native SDK subagents** - Use `agents` parameter in ClaudeAgentOptions for autonomous invocation, combined with `SubagentStop` hooks for validation

---

## References

### LangGraph
- [LangGraph Documentation](https://docs.langchain.com/langgraph)
- [Multi-Agent Workflows](https://blog.langchain.com/langgraph-multi-agent-workflows/)
- [Authentication & Authorization](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

### Claude Agent SDK
- [Claude Agent SDK Python](https://github.com/anthropics/claude-agent-sdk-python)
- [Hooks System Documentation](https://docs.claude.com/en/api/agent-sdk/overview)
- [Best Practices for Claude Code Subagents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)

### Research Papers
- [Governance-as-a-Service: Multi-Agent Framework for AI Compliance](https://arxiv.org/abs/2508.18765)
- [Control Plane as a Tool: Scalable Design Pattern for Agentic AI](https://arxiv.org/html/2505.06817v1)
- [Agentic AI Frameworks: Architectures, Protocols, and Design Challenges](https://arxiv.org/abs/2508.10146)

### Industry Resources
- [AI Agent Orchestration Patterns - Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Policy-Based AI Agent Governance - Airia](https://airia.com/agent-constraints-a-technical-deep-dive-into-policy-based-ai-agent-governance/)
- [Claude Code Hooks Multi-Agent Observability](https://github.com/disler/claude-code-hooks-multi-agent-observability)

---

*This research informs the SUBAGENT_REFACTOR_PLAN.md implementation strategy for Lightning Agents.*
