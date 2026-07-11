# Prompt — Data Ingestion and Indexing Pipeline

## Copy-paste prompt

You are a senior ML/data engineer.

Build a reliable ingestion pipeline for the **Aircraft Maintenance Decision Copilot**.

## Input data

Synthetic or authorized samples of:

- AMM
- MEL
- CDL
- TSM
- Engineering orders
- Historical defect records

Files may be PDF, text, HTML, CSV, or JSON.

## Required pipeline

```text
Source registration
→ file validation
→ parsing
→ document classification
→ metadata extraction
→ revision and applicability extraction
→ section-aware chunking
→ quality checks
→ embedding
→ vector indexing
→ graph relationship extraction
→ relational metadata storage
→ ingestion report
```

## Requirements

- Preserve page, section, table, title, revision, effective date, and source filename.
- Support idempotent re-ingestion.
- Detect duplicates.
- Mark superseded revisions.
- Quarantine malformed files.
- Generate deterministic chunk IDs.
- Never allow unauthorized web scraping.
- Use Tinyfish only for approved public sources and only when the integration is verified.
- Add a synthetic fallback dataset for the demo.
- Log latency, failures, and chunk counts.

## Deliverables

Implement:

```text
scripts/ingest.py
packages/retrieval/parsers/
packages/retrieval/chunking/
packages/retrieval/indexers/
tests/test_ingestion.py
docs/data-ingestion.md
```

## Acceptance criteria

- One command ingests the demo dataset.
- Re-running the command does not duplicate records.
- Every vector result maps back to exact source metadata.
- Failed documents produce a readable error report.
- The pipeline can run locally with Docker Compose.

First produce an implementation plan and file tree. Then produce code file by file.
