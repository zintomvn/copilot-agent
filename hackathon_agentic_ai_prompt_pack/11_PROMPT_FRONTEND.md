# Prompt — Demo Frontend

## Copy-paste prompt

You are a senior frontend engineer and product designer.

Build a clean hackathon demo interface for **Aircraft Maintenance Decision Copilot** using Next.js or React.

## Main screens

1. Case intake.
2. Analysis progress.
3. Evidence and citations.
4. Conflict and missing-information panel.
5. Structured recommendation report.
6. Human approval or rejection.
7. Agent trace and evaluation dashboard.
8. System status.

## Main workflow

```text
Create case
→ enter aircraft and defect context
→ run analysis
→ watch agent steps
→ inspect retrieved evidence
→ review warnings
→ approve or reject
→ export report
```

## UX requirements

- Make the safety boundary visible.
- Never present the AI result as an automatic dispatch authorization.
- Show citation metadata beside every important claim.
- Clearly distinguish:
  - verified evidence
  - inferred recommendation
  - uncertainty
  - missing information
  - conflicting evidence
- Show document type, section, revision, and relevance.
- Add a polished seeded demo case.
- Include loading, error, empty, and degraded states.
- Prioritize stability over animation.
- Use responsive layout.
- Avoid hard-coded secrets.

## Deliverables

```text
apps/web/app/
apps/web/components/
apps/web/lib/api.ts
apps/web/types/
apps/web/public/
apps/web/Dockerfile
```

## Acceptance criteria

- A judge can complete the golden path without instructions.
- Evidence is readable.
- The human approval gate is obvious.
- Failure states do not crash the page.
- The UI works with seeded synthetic data.
