# Prompt — Research the Problem and Design the Winning Solution

## Copy-paste prompt

You are a senior AI product researcher and aviation maintenance systems analyst supporting a hackathon team.

## Context

We are building an enterprise Agentic AI prototype for aircraft maintenance defect assessment.

The target users are Maintenance Control Center engineers and maintenance engineering teams. They currently search and cross-reference documents such as AMM, MEL, CDL, TSM, engineering orders, and historical defect records.

The system must not replace licensed engineering judgment. It should retrieve evidence, validate records, highlight inconsistencies, and produce explainable recommendations for human review.

## Your task

Create an evidence-driven solution brief that helps the team win the hackathon.

Cover:

1. The operational problem.
2. The specific user pain points.
3. Why a standard RAG chatbot is insufficient.
4. Why an agentic workflow is justified.
5. The proposed solution and golden-path workflow.
6. The top three demo use cases.
7. Competitive differentiation.
8. Enterprise adoption requirements.
9. Risks, limitations, and human-in-the-loop boundaries.
10. Measurable success metrics.
11. A one-sentence value proposition.
12. A 30-second pitch and a 2-minute pitch.

## Required reasoning constraints

- Do not invent aviation regulations, incident statistics, maintenance procedures, or document references.
- Clearly separate verified facts, project assumptions, and proposed design choices.
- Treat all maintenance outputs as decision support.
- Prioritize one narrow, high-quality use case over many incomplete features.
- Explain how citations, document applicability, version checks, and conflict detection improve trust.
- Explain why enterprise customers may require private deployment, access control, audit logs, and provider-independent architecture.

## Required output format

```markdown
# Research and Solution Brief

## Executive summary
## User and workflow
## Current pain points
## Why chatbot-only RAG is insufficient
## Proposed agentic solution
## Golden-path demo
## Top use cases
## Differentiation
## Enterprise requirements
## Success metrics
## Risks and limitations
## Value proposition
## 30-second pitch
## 2-minute pitch
## Assumptions that require validation
## Sources
```

For every factual external claim, include a reliable source. Do not cite a source that you have not actually checked.
