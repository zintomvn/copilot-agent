# Prompt — Agentic AI Architecture and Agent Loop

## Copy-paste prompt

You are a staff AI engineer specializing in production agent systems.

Design and implement the agent workflow for **Aircraft Maintenance Decision Copilot**.

## Required agent components

### Orchestrator

Controls state, routing, retries, termination, and final report generation.

### Suggested sub-agents

- Intake and normalization agent
- Applicability agent
- Documentation retrieval agent
- Defect validation agent
- Historical case agent
- Conflict and risk agent
- Report synthesis agent
- Citation verification agent
- Human approval gate

### Tools

- Relational lookup
- Vector retrieval
- Neo4j graph query
- Document section reader
- Historical case search
- Citation verifier
- Evaluation logger
- Audit logger

### Memory

- Short-lived run state
- User/session context
- Case evidence state
- No uncontrolled long-term memory
- Tenant-scoped persistence only

### Context

- Versioned system prompt
- Tool instructions
- Domain glossary
- Safety policy
- Output schema
- Retrieved evidence
- User-provided aircraft context

## Required agent loop

```text
Plan
→ retrieve evidence
→ inspect coverage
→ call specialist agents
→ detect conflicts
→ request missing information when necessary
→ verify citations
→ synthesize structured report
→ human approval gate
→ persist audit record
```

## Implementation constraints

- Prefer a state graph over an unconstrained autonomous loop.
- Set explicit maximum steps, retries, and timeouts.
- Use structured outputs validated with Pydantic or JSON Schema.
- Separate reasoning state from user-visible explanations.
- Do not expose hidden chain-of-thought.
- Store concise decision summaries and evidence links instead.
- Ensure final statements are grounded in retrieved evidence.
- Include a deterministic fallback when an LLM call fails.

## Deliverables

```text
packages/agents/state.py
packages/agents/graph.py
packages/agents/nodes/
packages/agents/prompts/
packages/agents/tools/
packages/agents/report.py
tests/test_agent_graph.py
docs/agent-architecture.md
```

## Acceptance criteria

- The happy path produces a valid analytical report.
- Missing information routes to a clarification state.
- Conflicting evidence produces a warning.
- Citation verification can block unsupported claims.
- The run always terminates.
- Human approval is mandatory before final submission status.
