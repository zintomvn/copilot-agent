# Prompt — Evaluation, LangSmith/Langfuse, Prometheus, and Grafana

## Copy-paste prompt

You are a senior LLM evaluation and observability engineer.

Design and implement evaluation for **Aircraft Maintenance Decision Copilot**.

## Evaluation goals

Measure whether the system:

- Retrieves the correct evidence.
- Avoids unsupported references.
- Detects missing information.
- Detects conflicts.
- Produces valid structured reports.
- Includes correct citations.
- Respects human approval.
- Completes within acceptable latency and cost.

## Required evaluation set

Create a small golden dataset with:

- Happy-path case.
- Missing aircraft context.
- No relevant evidence.
- Conflicting document revisions.
- Obsolete document.
- Prompt injection inside a document.
- Incorrect user-suggested reference.
- Tool timeout.
- Cross-tenant access attempt.

## Required metrics

- Recall@k for evidence retrieval.
- Precision of cited evidence.
- Citation validity rate.
- Unsupported claim rate.
- Structured output validity.
- Conflict detection accuracy.
- Missing-field detection accuracy.
- Task completion rate.
- Human-review agreement.
- End-to-end latency.
- LLM token usage and estimated cost.
- Tool error rate.

## Tooling strategy

- Use LangSmith for fast experiment comparison during the hackathon.
- Document Langfuse as a future self-hosted enterprise option.
- Export application metrics to Prometheus.
- Visualize system latency, memory, request rate, errors, and dependency health in Grafana.

## Deliverables

```text
data/eval/golden_cases.jsonl
scripts/run_eval.py
packages/observability/tracing.py
packages/observability/metrics.py
infra/prometheus/prometheus.yml
infra/grafana/
docs/evaluation.md
```

## Required outputs

- Evaluation rubric.
- Judge-friendly scorecard.
- Pass/fail thresholds.
- Dashboard specification.
- Example trace.
- Known weaknesses.
- Instructions to run evaluations locally.

Do not fabricate scores. Use placeholders until the evaluation is executed.
