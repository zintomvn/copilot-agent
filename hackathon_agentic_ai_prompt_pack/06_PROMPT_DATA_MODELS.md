# Prompt — Data Models for Relational, Vector, Graph, and Reports

## Copy-paste prompt

You are a senior data architect for safety-sensitive enterprise AI.

Design the data model for **Aircraft Maintenance Decision Copilot**.

## Required storage systems

- PostgreSQL or Supabase for relational records
- pgvector or Qdrant for embeddings
- Neo4j for relationships
- Object storage or local files for source documents
- Append-only audit records for agent activity

## Required entities

At minimum, model:

- Aircraft
- Aircraft type
- Tail number
- Defect report
- Defect observation
- Maintenance document
- Document revision
- Document section
- Applicability rule
- AMM task reference
- MEL item
- CDL item
- TSM procedure
- Engineering order
- Historical case
- Citation
- Retrieval result
- Agent run
- Agent step
- Tool call
- Recommendation
- Conflict
- Human review
- Evaluation case
- Evaluation result
- User
- Role
- Tenant

## Your task

Produce:

1. Entity relationship model.
2. PostgreSQL schema.
3. Neo4j node and edge model.
4. Vector payload schema.
5. JSON schema for the final analytical report.
6. Audit event schema.
7. Data lineage fields.
8. Versioning strategy.
9. Multi-tenant isolation strategy.
10. Sample synthetic records for one demo case.

## Constraints

- Every citation must map to a document revision and a precise section or chunk.
- Do not store an embedding without its source, version, tenant, and access scope.
- A recommendation must be linked to evidence and human review status.
- Support soft deletion and document supersession.
- Use UUIDs.
- Use UTC timestamps.
- Avoid storing secrets in application tables.

## Required output

Create:

```text
docs/data-model.md
packages/schemas/report.schema.json
infra/postgres/schema.sql
infra/neo4j/seed.cypher
data/synthetic/demo_case.json
```

Include comments in SQL and Cypher. Keep the hackathon schema implementable.
