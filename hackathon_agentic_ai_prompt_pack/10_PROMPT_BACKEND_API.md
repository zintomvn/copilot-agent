# Prompt — Backend API

## Copy-paste prompt

You are a senior Python backend engineer.

Build the FastAPI backend for **Aircraft Maintenance Decision Copilot**.

## Required endpoints

```text
POST   /api/v1/cases
GET    /api/v1/cases/{case_id}
POST   /api/v1/cases/{case_id}/analyze
GET    /api/v1/runs/{run_id}
GET    /api/v1/runs/{run_id}/stream
POST   /api/v1/runs/{run_id}/approve
POST   /api/v1/runs/{run_id}/reject
GET    /api/v1/runs/{run_id}/report
POST   /api/v1/documents/ingest
GET    /api/v1/health
GET    /api/v1/metrics
```

## Requirements

- Pydantic request and response models.
- Async endpoints where useful.
- Server-sent events or WebSocket streaming for run progress.
- Request IDs and trace IDs.
- Tenant and role checks.
- Audit logging.
- Structured error responses.
- Rate limiting hooks.
- Health checks for PostgreSQL, vector DB, Neo4j, and model provider.
- OpenAPI documentation.
- Environment-based configuration.
- No secrets in source code.
- Idempotency for analysis submission.
- Timeouts and retries for external services.

## Deliverables

```text
apps/api/main.py
apps/api/routes/
apps/api/dependencies/
apps/api/middleware/
apps/api/config.py
apps/api/errors.py
tests/api/
Dockerfile
```

## Acceptance criteria

- The API starts with one command.
- `/health` reports dependency status.
- The analyze endpoint starts an agent run.
- The client can stream step status.
- Approval and rejection are persisted.
- Errors are understandable and do not expose secrets.
