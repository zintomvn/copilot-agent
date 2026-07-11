# Hackathon Agentic AI Prompt Pack

## Project working title

**Aircraft Maintenance Decision Copilot**

An enterprise-oriented Agentic AI system that helps maintenance engineers retrieve approved technical references, validate defect records, identify inconsistencies, and generate explainable recommendations with citations.

## How to use this pack

1. Start with `01_MASTER_PLAN.md`.
2. Use `02_TASK_BOARD.md` to assign owners and track progress.
3. Copy one prompt file at a time into your coding/research assistant.
4. Save every output into the corresponding repository folder.
5. Do not let the agent invent aviation regulations, AMM/MEL references, metrics, partner capabilities, or demo results.
6. For the hackathon demo, use synthetic or organizer-provided data unless real maintenance documents are explicitly authorized.

## Recommended execution order

```text
Research and solution
        ↓
Product requirements and use cases
        ↓
Architecture and data model
        ↓
Data ingestion and retrieval
        ↓
Agent workflow and backend
        ↓
Frontend and enterprise security
        ↓
Evaluation and observability
        ↓
Cloud deployment
        ↓
Demo video, slides, report, GitHub cleanup
```

## Proposed technology stack

| Layer | Preferred technology |
|---|---|
| LLM and agent SDK | OpenAI models and OpenAI SDK |
| Agent orchestration | LangGraph / LangChain family or Deep Agents |
| Cloud | AWS VM and managed services where practical |
| Web extraction | Tinyfish, only for authorized public data |
| Graph database | Neo4j |
| Vector database | Qdrant or PostgreSQL with pgvector |
| Relational database | PostgreSQL / Supabase |
| Evaluation | LangSmith for rapid hackathon iteration |
| Enterprise observability | Langfuse as a self-hostable future option |
| Infrastructure monitoring | Prometheus and Grafana |
| Agent security | Antitech or the hackathon security partner, subject to verified capabilities |
| API | FastAPI |
| Frontend | Next.js or a simple React interface |
| Packaging | Docker and Docker Compose |

## Enterprise-first principles

- Human approval remains mandatory for safety-critical decisions.
- The agent recommends and validates; it does not independently release an aircraft.
- Every answer should include source references and uncertainty.
- Tenant data must be isolated.
- Models and storage should be replaceable.
- Private cloud or self-hosted deployment should be possible.
- Prompts, retrieval traces, tool calls, and evaluation results should be auditable.
