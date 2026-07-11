# Task Board

## Priority legend

- **P0**: Required for judging.
- **P1**: Strong differentiator.
- **P2**: Future work or optional polish.

## Execution board

| ID | Task | Owner | Priority | Dependency | Deliverable | Status |
|---|---|---:|---:|---|---|---|
| T01 | Research problem and solution |  | P0 | None | Research brief | Todo |
| T02 | Define product requirements |  | P0 | T01 | PRD and acceptance criteria | Todo |
| T03 | Design high-level architecture |  | P0 | T02 | Architecture document and diagram | Todo |
| T04 | Design data models |  | P0 | T02 | SQL, graph, vector, report schemas | Todo |
| T05 | Build ingestion pipeline |  | P0 | T04 | Parsed and indexed demo data | Todo |
| T06 | Build retrieval layer |  | P0 | T04, T05 | Hybrid search API | Todo |
| T07 | Build agent orchestration |  | P0 | T03, T06 | Agent graph and structured report | Todo |
| T08 | Build backend API |  | P0 | T07 | FastAPI endpoints | Todo |
| T09 | Build frontend |  | P0 | T08 | Demo UI | Todo |
| T10 | Add security and guardrails |  | P0 | T07, T08 | Security checks and audit log | Todo |
| T11 | Add evaluation |  | P0 | T07 | Golden set and scorecard | Todo |
| T12 | Add observability |  | P1 | T08 | Traces and system dashboard | Todo |
| T13 | Deploy to AWS |  | P1 | T08, T09 | Public or judge-accessible demo | Todo |
| T14 | Manage secrets and configuration |  | P0 | T08, T13 | `.env.example`, secret policy | Todo |
| T15 | Prepare GitHub repository |  | P0 | All code tasks | Reproducible repository | Todo |
| T16 | Record demo video |  | P0 | T09, T11 | 2–4 minute video | Todo |
| T17 | Build slides |  | P0 | T01–T16 | Final pitch deck | Todo |
| T18 | Write analytical report |  | P1 | T01–T17 | Technical report | Todo |
| T19 | Define monetization |  | P2 | T02 | Enterprise and Apify options | Todo |

## Critical path

```text
T01 → T02 → T03
            ├→ T04 → T05 → T06 → T07 → T08 → T09 → T16
            ├→ T10
            └→ T11
T08 + T09 → T13
All outputs → T15 → T17 → T18
```

## Suggested team split

| Role | Primary tasks |
|---|---|
| Product/research lead | T01, T02, T17, T18, T19 |
| Agent/backend engineer | T06, T07, T08, T10 |
| Data/ML engineer | T04, T05, T11, T12 |
| Frontend/demo engineer | T09, T13, T15, T16 |
