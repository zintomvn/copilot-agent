# Aircraft Maintenance Decision Copilot

Bounded LangChain/LangGraph pipeline that turns a defect case into an auditable evidence
package for authorized human review. Workflow exposes orchestration, specialist-agent actions,
tool calls, deterministic gates, bounded recovery loops, citations, and terminal state.

This project does **not** authorize dispatch, determine airworthiness, certify maintenance, or
release an aircraft to service.

> **Synthetic-data warning:** Demo corpus, cases, outputs, and evaluation results are synthetic
> hackathon evidence unless explicitly labelled otherwise. They are not approved maintenance
> instructions and must not be used for operational decisions.

## Requirements

- Python 3.11, 3.12, or 3.13
- `uv` (project uses `.venv`)
- OpenAI-compatible server at `http://localhost:20128/v1`
- Model `gpt-4o-mini`

## Install

PowerShell:

```powershell
uv venv .venv --python 3.12
uv sync --extra dev
Copy-Item .env.example .env
.\.venv\Scripts\Activate.ps1
```

Set `OPENAI_API_KEY` in `.env`. Local proxies that do not authenticate still need a non-empty
placeholder because the OpenAI client validates this field.

Confirm endpoint and model:

```powershell
(Invoke-RestMethod http://localhost:20128/v1/models).data.id
```

## Run two-example demo

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.cli demo --examples 2
```

Expected scenarios:

1. Supported synthetic evidence chain reaches `REVIEW_READY` for human review.
2. Missing critical aircraft/configuration input reaches `NEEDS_CLARIFICATION`.

Per-run JSONL traces are written under `logs/runs/`. Each trace records orchestrator and
specialist-agent order, tool calls, gate results, transitions, counters, token use, and terminal
state. Secrets, raw hidden reasoning, and API keys must never be logged.

## Evaluate many examples

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.evaluate --input data/eval_cases.jsonl
```

Evaluation retains passing and failing examples. Results report expected versus observed state,
latency, graph/model/tool counters, token use, and trace path. Synthetic status remains visible.

## Static checks and tests

```powershell
.\.venv\Scripts\ruff.exe check src tests
.\.venv\Scripts\python.exe -m compileall -q src tests
.\.venv\Scripts\pytest.exe
```

Tests cover schema contracts, component data flow, valid transition order, deterministic gates,
bounded cross-reference recovery, maximum-turn enforcement, and both demo scenarios. Workflow
uses explicit counters plus LangGraph recursion limit; configured turns are clamped to 40.

## Configuration budgets

Copy `.env.example` to `.env`, then tune limits without changing workflow logic. Defaults follow
architecture targets: 20 graph steps, 3 retrieval loops, 30 tool calls, 30 seconds runtime, and
hard maximum of 40 turns. Budget exhaustion produces controlled `ABSTAINED` or `FAILED` output,
never `REVIEW_READY`.

If the configured proxy rejects a listed model, `ALLOW_MODEL_FALLBACK=true` records the failed
model attempt and uses the deterministic planner/critic fallback. Use
`ALLOW_MODEL_FALLBACK=false` when model availability must be mandatory. `--offline` skips model
calls for repeatable local tests.

## Ingestion handoff

`aabw_agent.ingestion` defines frozen contracts for source registration, immutable raw artifacts,
controlled spans, quality gates, retrieval index records, and source snapshot manifests. The
synthetic corpus validates these contracts and each run pins `source_snapshot_id`, snapshot digest,
registry version, retrieval config version, and document count before planning starts.

Architecture source: [`contexts/outputs/architecture.md`](contexts/outputs/architecture.md),
sections 9 and 10.
