# Master Plan — Aircraft Maintenance Decision Copilot

## 1. Goal

Build a credible hackathon prototype of an enterprise Agentic AI copilot for aircraft defect assessment and maintenance decision support.

The prototype should demonstrate that an engineer can:

1. Enter or upload a defect description.
2. Retrieve relevant passages from AMM, MEL, CDL, TSM, engineering orders, or historical records.
3. Detect missing, conflicting, or suspicious information.
4. Receive an explainable recommendation with citations.
5. Review and approve the result before submission.
6. Inspect the agent trace, retrieval evidence, latency, token usage, and evaluation score.

## 2. Current status

Replace this section during execution.

```text
Research: Not started
Problem definition: Drafted
Architecture: Drafted
Data ingestion: Not started
Agent workflow: Not started
Backend: Not started
Frontend: Not started
Evaluation: Not started
Cloud deployment: Not started
Demo video: Not started
Slides: Not started
GitHub cleanup: Not started
```

## 3. Problem statement

Aircraft defect assessment and maintenance decision-making still depend heavily on manual review of technical documentation and engineer experience.

Maintenance Control Center and engineering teams must continuously cross-reference large document sets, including AMM, MEL, CDL, TSM, engineering orders, and historical defect records. As fleets grow and operational pressure increases, this manual process becomes slower and more vulnerable to missed information, inconsistent classifications, and incorrect references.

The project addresses four concrete problems:

- Engineers spend too much time searching across fragmented repositories.
- Defect records may contain incomplete or inconsistent information.
- Incorrect references may create delays or operational risk.
- Existing knowledge is difficult to reuse and audit.

## 4. Proposed solution

Develop an enterprise-ready Agentic AI copilot with the following workflow:

```text
Defect input
   ↓
Input validation and normalization
   ↓
Hybrid retrieval from vector, graph, relational, and document stores
   ↓
Specialized sub-agents analyze references, consistency, history, and risk
   ↓
Evidence aggregation and conflict detection
   ↓
Recommendation with source citations, uncertainty, and required human actions
   ↓
Engineer review and approval
   ↓
Audit log, evaluation, and observability
```

## 5. Core demo use case

**Input**

A maintenance engineer enters a defect description such as:

> During pre-flight inspection, the left navigation light is inoperative. Aircraft type and operational context are supplied.

**Expected system behavior**

- Normalize the defect.
- Retrieve the most relevant synthetic or approved MEL/AMM passages.
- Identify whether required fields are missing.
- Suggest the relevant maintenance references.
- Explain operational constraints using only retrieved evidence.
- Flag conflicts or low-confidence conclusions.
- Produce a structured report.
- Require engineer confirmation.

## 6. Proposed C1–C4 maturity architecture

These levels are proposed project maturity stages and can be renamed.

### C1 — Retrieval Copilot

- Search approved documents.
- Return cited passages.
- No autonomous action.

### C2 — Validation Agent

- Check defect fields.
- Detect mismatched references.
- Validate document version and applicability.

### C3 — Multi-Agent Decision Support

- Use specialized sub-agents.
- Compare document evidence, aircraft context, and historical cases.
- Produce a reasoned recommendation and uncertainty.

### C4 — Enterprise Operations Platform

- Private deployment.
- Role-based access.
- Tenant isolation.
- Evaluation, observability, governance, and continuous improvement.
- Integrations with maintenance systems through controlled APIs.

## 7. Major workstreams

| Workstream | Deliverable | Priority |
|---|---|---|
| Research and solution | Evidence-backed problem and differentiation | P0 |
| Product requirements | Scope, use cases, acceptance criteria | P0 |
| Architecture | High-level, C1–C4, ingestion, agent diagrams | P0 |
| Data layer | Schemas, vector, graph, relational model | P0 |
| Agent system | Orchestrator, sub-agents, tools, memory, context | P0 |
| Application | Backend API and usable UI | P0 |
| Evaluation | Golden set, metrics, trace evaluation | P0 |
| Security | Guardrails, secrets, access, audit | P0 |
| Cloud | Reproducible deployment | P1 |
| Observability | LangSmith/Langfuse, Prometheus/Grafana | P1 |
| Demo | Stable script and recorded video | P0 |
| Slides and report | Clear story and evidence | P0 |
| GitHub | Clean, reproducible repository | P0 |
| Business model | Enterprise path and optional Apify distribution | P2 |

## 8. Suggested repository structure

```text
aircraft-maintenance-copilot/
├── README.md
├── LICENSE
├── .env.example
├── docker-compose.yml
├── docs/
│   ├── problem-statement.md
│   ├── architecture.md
│   ├── evaluation.md
│   └── demo-script.md
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic/
│   └── eval/
├── apps/
│   ├── web/
│   └── api/
├── packages/
│   ├── agents/
│   ├── retrieval/
│   ├── schemas/
│   ├── security/
│   └── observability/
├── infra/
│   ├── docker/
│   ├── aws/
│   ├── prometheus/
│   └── grafana/
├── scripts/
│   ├── ingest.py
│   ├── seed_demo.py
│   └── run_eval.py
└── tests/
```

## 9. Hackathon execution strategy

### Phase A — Win the story

- Finalize a narrow, believable use case.
- Explain why a normal chatbot is insufficient.
- Show how the agent uses tools, evidence, validation, and human approval.
- Define measurable success.

### Phase B — Build the golden path

- Implement one stable end-to-end flow.
- Prefer deterministic structured outputs.
- Use a small, curated demo dataset.
- Add graceful fallbacks when tools fail.

### Phase C — Prove enterprise potential

- Add audit logs.
- Show model/provider abstraction.
- Show private deployment path.
- Add evaluation and observability.
- Explain security boundaries.

### Phase D — Package the result

- Record the demo before final slide polishing.
- Include architecture and trace screenshots.
- Make repository setup reproducible.
- State limitations honestly.

## 10. Definition of done

The project is demo-ready when:

- A reviewer can run the app from the README.
- The main use case works three consecutive times.
- Every recommendation has citations.
- Unsupported conclusions are blocked or marked uncertain.
- The UI shows missing information and conflicts.
- An agent trace is visible.
- A small evaluation set produces documented metrics.
- No secret is committed.
- The video, slides, and GitHub links are ready.
