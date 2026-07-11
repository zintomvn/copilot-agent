# Prompt — Hybrid Retrieval Engine

## Copy-paste prompt

You are a senior retrieval engineer.

Implement a hybrid retrieval layer for the **Aircraft Maintenance Decision Copilot**.

## Retrieval sources

- Vector search from Qdrant or pgvector
- Keyword or full-text search
- Neo4j graph traversal
- PostgreSQL filters
- Historical case lookup

## Query inputs

- Natural-language defect description
- Aircraft type
- Tail number
- Date or operational context
- ATA chapter when known
- Document types to include
- Tenant and access scope

## Required behavior

1. Normalize the query.
2. Apply hard metadata filters.
3. Run vector and lexical retrieval.
4. Use graph expansion for related tasks, items, applicability, and historical cases.
5. Merge and deduplicate results.
6. Rerank evidence.
7. Detect document revision conflicts.
8. Return structured evidence with confidence and source metadata.

## Safety constraints

- Retrieval must not silently cross tenant boundaries.
- Obsolete documents must be marked.
- Low-confidence retrieval must trigger a clarification or uncertainty status.
- Never fabricate a document reference.
- The final answer must only cite returned evidence.

## Deliverables

```text
packages/retrieval/service.py
packages/retrieval/models.py
packages/retrieval/reranker.py
packages/retrieval/conflict_detector.py
tests/test_retrieval.py
docs/retrieval.md
```

## Required API output

Return JSON containing:

```json
{
  "query_id": "uuid",
  "normalized_query": {},
  "results": [],
  "conflicts": [],
  "coverage": {},
  "latency_ms": 0
}
```

Include unit tests for filtering, citation traceability, duplicate handling, obsolete revision detection, and no-result fallback.
