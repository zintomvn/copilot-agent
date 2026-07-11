# Prompt — Product Requirements and Demo Scope

## Copy-paste prompt

You are a senior product manager for enterprise AI systems.

Create a hackathon-ready Product Requirements Document for an **Aircraft Maintenance Decision Copilot**.

## Product objective

Help maintenance engineers retrieve approved technical references, validate defect entries, detect inconsistencies, and generate an explainable recommendation with citations and mandatory human approval.

## Required users

- Maintenance Control Center engineer
- Maintenance engineer
- System administrator
- Auditor or safety reviewer

## Required product behavior

- Accept a defect description and aircraft context.
- Validate mandatory fields.
- Retrieve relevant synthetic or approved documentation.
- Return citations with document metadata.
- Detect conflicting, obsolete, or weak evidence.
- Produce a structured analytical report.
- Require human approval.
- Save an audit trail.
- Expose agent traces and evaluation results for the demo.

## Scope constraint

The hackathon prototype should support one polished end-to-end use case. Additional use cases should be documented as future work.

## Your task

Produce:

1. Product vision.
2. User personas.
3. Jobs to be done.
4. Functional requirements.
5. Non-functional requirements.
6. User stories.
7. Golden-path user journey.
8. Error and fallback journeys.
9. In-scope and out-of-scope items.
10. Acceptance criteria.
11. Demo data requirements.
12. A P0/P1/P2 backlog.
13. Definition of done.

## Safety constraints

- Never claim the system independently authorizes aircraft dispatch.
- Human approval is required.
- Unsupported recommendations must be blocked or marked uncertain.
- Documents must be versioned and attributable.
- Use synthetic data when real documents are unavailable or restricted.

## Required output format

Write a complete `docs/product-requirements.md` file. Use tables for requirements and acceptance criteria. Give every requirement an ID such as `FR-01`, `NFR-01`, and `AC-01`.
