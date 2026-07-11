# Prompt — End-to-End Integration and Final Test

## Copy-paste prompt

You are the technical lead responsible for final hackathon integration.

Integrate and validate **Aircraft Maintenance Decision Copilot**.

## Goal

Produce one stable end-to-end golden path and a documented fallback.

## Required test sequence

1. Start all services.
2. Verify health checks.
3. Seed synthetic documents and one demo case.
4. Create a case through the UI.
5. Run agent analysis.
6. Verify retrieval evidence.
7. Verify citations.
8. Verify conflict or missing-field behavior.
9. Verify structured report schema.
10. Verify human approval.
11. Verify audit record.
12. Verify LangSmith or Langfuse trace.
13. Verify Prometheus metrics.
14. Verify Grafana dashboard.
15. Run the evaluation suite.
16. Restart services and repeat.
17. Run the demo three consecutive times.

## Failure policy

- Disable unstable optional features.
- Prefer mocked or seeded dependencies over broken live integrations.
- Keep the core analysis path real.
- Document every mock.
- Create a fallback video and screenshots.

## Deliverables

```text
docs/integration-test.md
docs/demo-checklist.md
scripts/smoke_test.py
tests/e2e/
```

## Final report

Return a table with:

- Component.
- Status.
- Verification method.
- Known issue.
- Demo fallback.
- Owner.

Do not mark a component complete without a reproducible verification step.
