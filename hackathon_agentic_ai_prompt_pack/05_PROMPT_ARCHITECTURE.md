# Prompt — High-Level, C1–C4, and Enterprise Architecture

## Copy-paste prompt

You are a principal enterprise AI architect.

Design the architecture for a hackathon prototype called **Aircraft Maintenance Decision Copilot**.

## Preferred technologies

- AWS for cloud and VM hosting
- OpenAI models and SDK
- LangGraph, LangChain family, or a Deep Agent pattern
- Tinyfish for authorized public web extraction, only when needed
- Neo4j for graph relationships
- Qdrant or PostgreSQL with pgvector for vector retrieval
- PostgreSQL or Supabase for relational data
- LangSmith for rapid evaluation during the hackathon
- Langfuse as a future self-hosted enterprise observability option
- Prometheus and Grafana for infrastructure metrics
- FastAPI backend
- Next.js or React frontend
- Docker Compose for local reproducibility
- Antitech or the named security partner only where verified

## Required architecture views

1. System context diagram.
2. Container-level architecture.
3. Component architecture.
4. C1–C4 maturity model:
   - C1 retrieval copilot
   - C2 validation agent
   - C3 multi-agent decision support
   - C4 enterprise operations platform
5. Data ingestion flow.
6. Online query flow.
7. Agent orchestration flow.
8. Security and trust boundaries.
9. Observability and evaluation flow.
10. Local demo deployment.
11. AWS deployment.
12. Future private-cloud or self-hosted deployment.

## Architecture principles

- Human-in-the-loop.
- Evidence-first responses.
- Provider abstraction.
- Tenant isolation.
- Least privilege.
- Auditable tool calls.
- Versioned prompts and schemas.
- Graceful degradation.
- No hidden autonomous maintenance action.

## Required output

Create a complete `docs/architecture.md` containing:

- Architecture decisions.
- Mermaid diagrams for every required view.
- Component responsibilities.
- API boundaries.
- Data ownership.
- Failure modes.
- Scalability path.
- Trade-offs.
- A “hackathon implementation” column and a “production evolution” column.

Do not invent capabilities for any partner product. Mark uncertain integrations as placeholders requiring verification.
