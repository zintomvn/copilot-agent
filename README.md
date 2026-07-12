# Aircraft Maintenance Decision Copilot

Evidence-gated AI copilot for the AABW aircraft-maintenance demo. The system turns a
synthetic aircraft defect case into a traceable evidence package for authorized human review.

It shows:

- visible agent workflow: goal -> plan -> tools -> act -> verify -> human review;
- LangGraph bounded workflow states and deterministic safety gates;
- Deep Agents supervisor with read-only tools, subagents, and memory;
- claim-level citations, rejected evidence, cross-reference handling, conflicts, and abstention;
- Langfuse tracing/evaluation when credentials are configured;
- React UI for live judging demo.

This project does **not** authorize dispatch, determine airworthiness, certify maintenance, or
release an aircraft to service. All demo data are synthetic unless explicitly labelled otherwise.

## Demo Mode

Use one of these modes.

| Mode | When to use | What to set |
| --- | --- | --- |
| Offline deterministic | Safest live demo, no model/network dependency | UI toggle `Offline fallback` on, or CLI `--offline` |
| OpenAI API online | Deep Agents + model calls + optional LLM judge | `OPENAI_BASE_URL=https://api.openai.com/v1`, valid `OPENAI_API_KEY` |
| Local proxy | Only if you are running an OpenAI-compatible proxy yourself | `OPENAI_BASE_URL=http://localhost:20128/v1` |

If this command fails:

```powershell
(Invoke-RestMethod http://localhost:20128/v1/models).data.id
```

it only means the local proxy is not running. For OpenAI cloud, do not use that localhost URL.
Set:

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-...
```

Then check safely without printing secrets:

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.env_doctor --check-network
```

## Install

PowerShell:

```powershell
uv venv .venv --python 3.12
uv sync --extra dev
Copy-Item .env.example .env

cd frontend
npm install
cd ..
```

Edit `.env`. Minimal safe offline demo config:

```env
OFFLINE=true
ALLOW_MODEL_FALLBACK=true
ENABLE_DEEP_AGENT=true
ENABLE_LANGFUSE=false
ENABLE_LLM_JUDGE=false
```

Online OpenAI + Langfuse demo config:

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...

OFFLINE=false
ALLOW_MODEL_FALLBACK=true
ENABLE_DEEP_AGENT=true
DEEP_AGENT_MODEL=
PROMPT_PROFILE=safety_default

ENABLE_LANGFUSE=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com

ENABLE_LLM_JUDGE=true
LLM_JUDGE_MODEL=gpt-4o-mini

MAX_RUNTIME_SECONDS=90
MODEL_TIMEOUT_SECONDS=60
PER_TOOL_TIMEOUT_SECONDS=8
RETRIEVAL_TOP_K=13
```

Boolean values must be exactly `true` or `false`.

## Prepare Synthetic Demo Data

Generate the 12-case benchmark/demo dataset:

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.synthetic_data `
  --corpus-out data\benchmark_corpus.json `
  --cases-out data\benchmark_cases.jsonl
```

The generated data covers:

- supported evidence chain -> `REVIEW_READY`;
- missing required input -> `NEEDS_CLARIFICATION`;
- superseded entered reference -> `NEEDS_CLARIFICATION`;
- wrong configuration/effectivity -> `ABSTAINED`;
- unresolved mandatory cross-reference -> `ABSTAINED`;
- conflicting current sources -> `ESCALATED`;
- unverified source rejection -> `ABSTAINED`;
- historical-context-only abstention;
- TSM, CDL, and engineering-procedure supported paths;
- tool-budget exhaustion.

## Run The Chatbot Demo UI

Terminal 1, start API:

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.api --host 127.0.0.1 --port 8002
```

Terminal 2, start React UI:

```powershell
cd frontend
npm run dev -- --port 5173 --strictPort
```

Open:

```text
http://127.0.0.1:5173
```

The API automatically uses `data/benchmark_cases.jsonl` and `data/benchmark_corpus.json` when
they exist.

The UI is a chatbot. Every message calls `POST /chat`, which runs the actual workflow agent,
domain tools, deterministic gates, and local trace logging. When `ENABLE_LANGFUSE=true`, the same
run also creates a Langfuse trace with Deep Agents/model spans and tool spans.

## One-Minute Demo Script

Use the UI and follow this order.

1. Select `BM-READY-LG-001`.
2. Keep `Offline fallback` off when you want Deep Agents + Langfuse tracing. Turn it on only for
   the no-network backup demo.
3. Send the chat message already filled in the composer.
4. Show the assistant answer: final state, plan, tool calls, gates, evidence, claims, notice.
5. Open the Langfuse trace link in the right inspector when available.
6. Point out tool spans such as `search_semantic`, `lookup_document`, `search_lexical`,
   `search_historical_cases`, and `resolve_cross_reference`.
7. Show the right inspector: workflow nodes, tool calls, accepted evidence, cited claims.

Then show one negative case:

- `BM-SUPERSEDED-REF-001`: stale entered reference is blocked.
- `BM-CONFLICT-HYD-001`: conflicting current sources route to `ESCALATED`.
- `BM-UNRESOLVED-XREF-001`: missing mandatory cross-reference routes to `ABSTAINED`.

Pitch line to say:

```text
The agent does not just retrieve text. It plans a bounded evidence search, uses controlled tools,
checks applicability, revision and approval gates, follows mandatory references, cites every claim,
and stops safely when the evidence is incomplete or conflicting.
```

## Run Unit Tests

```powershell
.\.venv\Scripts\ruff.exe check src tests
.\.venv\Scripts\python.exe -m compileall -q src tests
.\.venv\Scripts\pytest.exe
```

Current local result: `29 passed`.

## Run Benchmarks

Each benchmark case now emits a Langfuse-ready evaluator suite. Important score names:

- routing: `final_state`, `safe_non_review_ready_recall`, `review_ready_precision_guard`;
- citation: `citations_resolve`, `citation_coverage`, `no_rejected_evidence_leakage`;
- evidence gates: `approval_gate_compliance`, `revision_gate_compliance`,
  `applicability_gate_compliance`, `gate_results_review_ready`;
- safety behavior: `required_input_detection`, `superseded_reference_detection`,
  `cross_reference_completion`, `conflict_escalation`;
- observability: `trace_complete`, `local_trace_file_exists`, `tool_trace_visibility`;
- budget: `graph_step_cap`, `tool_call_cap`, `token_cap`, `runtime_target_configured`.

Full deterministic backup benchmark:

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.benchmark `
  --generate-data `
  --corpus data\benchmark_corpus.json `
  --cases data\benchmark_cases.jsonl `
  --output-dir artifacts\benchmark-offline `
  --offline `
  --models offline-fallback `
  --prompt-profiles safety_default,strict_abstention,retrieval_broad
```

Online Langfuse experiment with multiple models and prompt profiles:

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.env_doctor --check-network

.\.venv\Scripts\python.exe -m aabw_agent.benchmark `
  --corpus data\benchmark_corpus.json `
  --cases data\benchmark_cases.jsonl `
  --output-dir artifacts\langfuse-experiment `
  --models gpt-4o-mini,gpt-4.1-mini `
  --prompt-profiles safety_default,strict_abstention,retrieval_broad
```

Artifacts:

- `benchmark_summary.json`: model/prompt matrix, pass rate, latency, score means, category means.
- `benchmark_results.jsonl`: full per-case workflow result, checks, scores, trace ids.
- `benchmark_scores.csv`: one row per score, ready for spreadsheet/appendix charts.
- `langfuse_scores_snapshot.json`: fetched score snapshot when Langfuse is enabled.

Current observed results:

- Offline evaluator matrix: `36/36 passed`
- `review_ready_precision=1.0`
- `safe_non_review_ready_recall=1.0`
- Current local environment has `ENABLE_LANGFUSE=false`, so local score upload was skipped.

If `ENABLE_LANGFUSE=true`, deterministic scores are sent to Langfuse and fetched back into
`langfuse_scores_snapshot.json`. If `ENABLE_LLM_JUDGE=true`, the benchmark also asks the judge
model to score human-authority and citation-boundary compliance.

For the hackathon experiment, make sure `.env` contains:

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...

OFFLINE=false
ENABLE_DEEP_AGENT=true
ENABLE_LANGFUSE=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com

ENABLE_LLM_JUDGE=true
LLM_JUDGE_MODEL=gpt-4o-mini

MAX_RUNTIME_SECONDS=90
MODEL_TIMEOUT_SECONDS=60
RETRIEVAL_TOP_K=13
```

Then rerun the online benchmark above and open Langfuse. Filter traces by
`environment=hackathon-demo`, tags `aabw`, and score names such as `final_state`,
`approval_gate_compliance`, `citation_coverage`, and `conflict_escalation`.

## CLI Demo

Run a quick two-case demo:

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.cli demo --examples 2 --offline
```

Run the full benchmark dataset through the evaluator:

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.evaluate `
  --input data\benchmark_cases.jsonl `
  --offline `
  --output artifacts\evaluation-results.jsonl
```

## PDF Ingestion Later

Create a manifest JSON with controlled metadata, then run:

```powershell
.\.venv\Scripts\python.exe -m aabw_agent.pdf_ingest `
  --pdf data\uploads\sample.pdf `
  --manifest data\uploads\sample.manifest.json `
  --output data\ingested_corpus.json
```

Then set:

```env
CORPUS_PATH=data/ingested_corpus.json
```

The ingest path is conservative: approval, revision, effectivity, and source authority must come
from the manifest, not from the LLM.

## Troubleshooting

### `Unable to connect to localhost:20128`

You are configured for a local proxy that is not running. Either start that proxy, or use OpenAI:

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-...
```

### UI cannot call API

Make sure API is running:

```powershell
Invoke-RestMethod http://127.0.0.1:8002/health
```

Then reload `http://127.0.0.1:5173`.

### Need a no-risk live demo

Use offline mode. The UI still shows the full agentic workflow, tool calls, deterministic gates,
evidence, citations, and terminal states using synthetic data.

## Submission Notes

Only claim tools that are actually used in your demo and repository. Current implemented tools:

- Python
- FastAPI
- React
- LangChain
- LangGraph
- Deep Agents
- OpenAI API or OpenAI-compatible endpoint, when online mode is used
- Langfuse, when `ENABLE_LANGFUSE=true`

Do not claim AWS, OpenSearch, RDS, S3, Neo4j, or production airline integrations unless you add and
show real integrations for them.
