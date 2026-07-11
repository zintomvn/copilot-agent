# Problem Statement Insights — Aircraft Maintenance Decision Copilot

> **Purpose:** Slide-ready problem framing and reusable context for an AI agent.  
> **Project context:** Agentic AI Build Week 2026 — Aircraft Maintenance Decision Copilot.  
> **Scope:** Problem understanding only. This document does not claim that the proposed system is certified, production-ready, or authorized to make maintenance, dispatch, airworthiness, or release-to-service decisions.  
> **Evidence discipline:** Claims are labelled as **Brief**, **Verified Context**, **Assumption**, or **Design Implication**.

---

## 1. Executive Problem Statement

### Recommended one-line problem statement

**Aircraft maintenance engineers lose time and face review risk because assessing a defect requires manually locating, cross-checking, and validating fragmented technical evidence before an authorized human can make a decision.**

### Stronger insight-led version

**The core problem is not document search. It is determining whether the retrieved evidence is current, applicable, complete, mutually consistent, and sufficient for an authorized engineer to review a defect safely.**

### Slide headline

> **Aircraft defect assessment is an evidence-validation problem—not just a search problem.**

---

## 2. The User, Goal, and Broken Workflow

### Primary users

- Maintenance Control Center (MCC) engineers.
- Maintenance engineering teams.
- Authorized reviewers or certifying staff.
- Technical publication and quality teams as supporting stakeholders.

### User goal

The user needs to turn a defect report into a review-ready package that:

1. identifies relevant approved technical references;
2. confirms that those references apply to the aircraft and configuration;
3. checks that the references are current and complete;
4. exposes missing, conflicting, or inconsistent information;
5. preserves evidence for authorized human review.

### Where the workflow breaks

A defect assessment may require engineers to move across:

- Aircraft Maintenance Manual (AMM);
- Minimum Equipment List (MEL);
- Configuration Deviation List (CDL);
- Troubleshooting Manual (TSM);
- engineering orders or procedures;
- historical defect and maintenance records.

The engineer must reconstruct one evidence chain across different repositories, formats, document types, revisions, and cross-references. The process is therefore slower and more error-prone than a single document lookup.

---

## 3. Highest-Priority Problem Insights

The following insights should be prioritized in the pitch and slides. They are ordered by judge relevance and product importance.

### Insight 1 — Fragmentation forces engineers to manually reconstruct an evidence chain

**Evidence status:** Brief.

The required evidence is distributed across several technical-document families and historical records. The engineer does not simply search for one answer; they must assemble a coherent chain of evidence across sources.

**Why this matters**

- Search time is distributed across multiple repositories.
- Important conditions may be located outside the first retrieved document.
- The final assessment depends on how the sources relate to one another, not only on whether a relevant paragraph was found.
- Prior reasoning may be difficult to reconstruct if the evidence chain is not recorded.

**Slide-ready wording**

> **One defect can require a manual evidence chain across AMM, MEL, CDL, TSM, engineering procedures, and historical records.**

**Design implication**

The product must retrieve, connect, and preserve evidence across sources rather than return isolated search results.

---

### Insight 2 — Relevance is not the same as applicability

**Evidence status:** Design inference supported by controlled-maintenance-data requirements in the research brief.

A passage can be semantically relevant while still being unusable because it is:

- for a different aircraft or configuration;
- outside the correct effectivity range;
- superseded by a newer revision;
- not approved for the target workflow;
- missing required contextual metadata.

**Why this matters**

A conventional search engine or basic RAG system optimizes for similarity. Maintenance review also requires deterministic checks for applicability, approval state, and currentness.

**Slide-ready wording**

> **A relevant answer can still be the wrong answer for this aircraft, configuration, or revision.**

**Design implication**

Applicability and revision gates must run before retrieved text is allowed to support a recommendation.

---

### Insight 3 — The defect entry itself may be incomplete or inconsistent

**Evidence status:** Brief; independently supported as general record-quality friction in the research brief.

The workflow is not only about answering an engineer's question. The record being submitted may contain:

- incomplete defect context;
- inconsistent classification;
- an incorrect or missing AMM/MEL reference;
- a reference that does not match the defect description;
- dispatch-condition fields that require human correction.

**Why this matters**

A search-only assistant may provide useful information while failing to challenge an incorrect record. The highest-value intervention happens **before submission**, when missing or inconsistent fields can still be corrected.

**Slide-ready wording**

> **The system must validate what the engineer entered—not only answer what the engineer asked.**

**Design implication**

The product should parse the defect into a typed record, run deterministic validation, and move the case into a correction or escalation state when required.

---

### Insight 4 — Cross-references make the task inherently multi-step

**Evidence status:** Brief / Assumption to validate on authorized enterprise documents.

One document may require the engineer to consult another procedure, condition, limitation, or operational check. A first retrieval can therefore reveal the need for a second targeted retrieval.

**Why this matters**

- A correct first result may still produce an incomplete assessment.
- Long-context prompting is not a reliable substitute for explicit follow-up retrieval.
- The workflow requires state: what has been found, what remains missing, and why another search is needed.

**Slide-ready wording**

> **The first correct document may only reveal the next document that must be checked.**

**Design implication**

An agentic workflow is justified when it can plan follow-up searches, resolve required cross-references, verify completeness, and stop when evidence remains insufficient.

---

### Insight 5 — Operational pressure increases the cost of missed information

**Evidence status:** Brief; fatigue and pressure are verified general human-factor concerns, not project-specific incident statistics.

As fleets and workload grow, engineers must perform the same evidence-assembly and validation work under greater time pressure. Fatigue, distraction, workload, and communication gaps can increase the chance that relevant information is overlooked.

**Important framing**

The problem is **not** that engineers lack expertise. The problem is that expert attention is consumed by repetitive evidence gathering and checking under operational pressure.

**Slide-ready wording**

> **Expert judgment is scarce; manual evidence assembly consumes it.**

**Design implication**

The system should reduce search and checking burden while preserving active human review and avoiding automation bias.

---

### Insight 6 — A polished answer without provenance is not decision-ready

**Evidence status:** Research-backed design insight.

A response may look confident while:

- citing a source that does not support the claim;
- mixing current and superseded evidence;
- hiding a conflict between documents;
- omitting the checks that were performed;
- failing to record the human correction or approval.

**Why this matters**

In a controlled maintenance workflow, trust comes from inspectable evidence and reproducible checks—not from fluent language or a model confidence score.

**Slide-ready wording**

> **Trust requires claim-level evidence, visible checks, and a reconstructable human decision trail.**

**Design implication**

Each material claim should bind to exact evidence; conflicts and abstentions should be visible; inputs, revisions, checks, and human actions should be recorded.

---

## 4. Root-Cause Chain

Use this chain to explain the problem without jumping prematurely to technology.

```text
Fragmented technical sources
        ↓
Manual search and cross-referencing
        ↓
Applicability, revision, and completeness checks performed across tools
        ↓
Missing or inconsistent defect references can survive until review
        ↓
More rework, slower decisions, and avoidable operational-review risk
        ↓
Authorized engineers spend expert attention assembling evidence instead of reviewing it
```

### Root cause in one sentence

**The current workflow lacks a unified, evidence-aware validation layer that can connect approved sources, enforce applicability and revision checks, and challenge incomplete defect entries before submission.**

---

## 5. Problem Layers

### Surface problem

Engineers spend too much time searching maintenance documentation.

### Deeper workflow problem

The evidence needed for one assessment is fragmented and must be manually cross-checked.

### Safety and trust problem

A retrieved passage may be stale, inapplicable, incomplete, contradictory, or unsupported.

### Governance problem

The workflow must preserve human authority, approved-source controls, and an auditable record of how the draft assessment was produced and reviewed.

### Product opportunity

Create an evidence-gated review workflow that turns a defect entry into an applicability-checked, conflict-aware, fully cited package for authorized human review.

---

## 6. Why Basic Search or Chatbot-Only RAG Is Insufficient

| Failure mode | Why it matters | Required capability |
|---|---|---|
| Semantic relevance is mistaken for applicability | A relevant passage may be wrong for the aircraft, configuration, effectivity, or revision | Deterministic applicability and revision gate |
| Retrieved text is treated as proof of correctness | RAG can still produce unsupported or contradictory claims | Claim-to-evidence validation and abstention |
| Citation is present but does not support the adjacent claim | A link alone does not prove grounding | Atomic claims with exact, resolvable evidence |
| One retrieval omits a required cross-reference | The initial document may be only one part of the evidence chain | Targeted follow-up retrieval and completeness checks |
| Conflicting sources are silently merged | The system can hide a safety-relevant disagreement | Explicit conflict object and human escalation |
| Missing input fields are handled in prose only | The model may mention a missing field without enforcing it | Typed schema and deterministic validation |
| No workflow state is preserved | A chat answer does not prove which checks ran or why the system stopped | Bounded workflow, state transitions, and event trace |

### Key differentiation statement

> **A chatbot finds information. An evidence-gated copilot verifies whether the information can support this specific defect record.**

---

## 7. Consequences of the Current Workflow

Use only qualitative consequences unless the team has measured and documented a baseline.

### Operational consequences

- Longer time to assemble a review-ready defect package.
- Rework when a reference, classification, or required field is incomplete.
- Delays when evidence must be searched again or corrected.
- Inconsistent review quality across repositories and hand-offs.

### Risk consequences

- A wrong or superseded reference may appear plausible.
- A required linked procedure or condition may be missed.
- Conflicting evidence may not be surfaced clearly.
- A final reviewer may have insufficient visibility into how the recommendation was produced.

### Organizational consequences

- Expert time is spent on repetitive evidence gathering.
- Knowledge remains fragmented across systems and historical records.
- Prior assessments are difficult to reuse safely without provenance and applicability checks.
- Audit and quality teams may need to reconstruct decisions from incomplete traces.

### Claims that must not be made without measurement

Do not claim:

- a specific percentage of time saved;
- a specific reduction in maintenance errors;
- a specific incident or delay rate at the partner airline;
- production accuracy or aviation certification;
- that the AI can approve dispatch, airworthiness, or release to service;
- that an external vendor lacks a capability unless independently verified.

---

## 8. Recommended Slide Content

## Option A — One-slide problem story

### Headline

**Aircraft defect assessment is an evidence-validation problem—not just a search problem.**

### Body

**MCC and maintenance engineers must manually:**

1. search fragmented AMM, MEL, CDL, TSM, engineering, and historical sources;
2. verify aircraft applicability, configuration, revision, and approval state;
3. follow cross-references and detect missing or conflicting information;
4. correct the defect record before an authorized reviewer can decide.

### Insight callout

> **A semantically relevant passage can still be stale, inapplicable, incomplete, or unsupported.**

### Consequence

**Expert time is consumed assembling evidence under operational pressure, increasing review friction and the chance of missed information.**

### Bottom-line opportunity

**Turn each defect entry into a traceable, applicability-checked evidence package for authorized human review.**

---

## Option B — Two-slide problem story

### Slide 1 — The workflow failure

**Title:** One defect. Many sources. One manual evidence chain.

- Defect assessment spans AMM, MEL, CDL, TSM, engineering orders, and historical records.
- Engineers must search, interpret, and cross-reference evidence across repositories.
- Defect classifications and entered references may be incomplete or inconsistent.
- Workload and time pressure increase the chance that relevant information is missed.

**Speaker line:**

> “We discovered that engineers are not simply searching for a procedure. They are manually reconstructing and validating an evidence chain.”

### Slide 2 — The deeper insight

**Title:** Finding a relevant passage does not prove it is usable.

- Is it approved?
- Is it current?
- Does it apply to this aircraft and configuration?
- Are required linked procedures present?
- Do any sources conflict?
- Can every claim be traced to exact evidence?

**Speaker line:**

> “This is why a chatbot with citations is not enough. The workflow needs applicability gates, cross-reference validation, conflict detection, and safe human escalation.”

---

## 9. Forty-Second Problem Narrative

> **MCC and maintenance engineers assess aircraft defects by searching across AMM, MEL, CDL, TSM, engineering procedures, and historical records. We discovered that the bottleneck is not simply finding a relevant paragraph. Engineers must prove that each reference is current, applicable to the aircraft and configuration, complete with its required cross-references, and consistent with the defect entry. Because this validation is manual and fragmented, expert time is consumed assembling evidence under operational pressure, and incomplete or incorrect references can create rework, delay, or review risk.**

---

## 10. Concise Problem–Insight–Opportunity Chain

### Problem

Aircraft defect review depends on manual search and cross-referencing across fragmented technical sources.

### Insight

A relevant document is not necessarily valid evidence for the specific aircraft, revision, configuration, and defect record.

### Opportunity

Build an agentic, evidence-gated review layer that retrieves approved sources, verifies applicability and completeness, exposes conflicts, and produces a cited package for authorized human review.

---

## 11. Problem Statement Variants

### Variant 1 — Judge-friendly

**MCC engineers must manually assemble and validate evidence across fragmented maintenance documents before a defect can be reviewed, making the process slow, inconsistent, and vulnerable to missing or incorrect references.**

### Variant 2 — Safety and trust focused

**Aircraft defect assessment lacks a unified way to verify that technical references are approved, current, applicable, complete, and consistent before they support an engineering review.**

### Variant 3 — Workflow focused

**The current defect-review workflow requires engineers to search multiple repositories, follow cross-document dependencies, and manually validate the submitted record, consuming expert time and creating avoidable rework.**

### Variant 4 — Agentic-solution bridge

**A single defect can trigger a chain of searches and checks across maintenance sources, but current workflows do not automatically plan the follow-up retrievals, validate applicability, detect conflicts, or stop when evidence is insufficient.**

### Recommended final version

> **Aircraft maintenance engineers lose time and face review risk because assessing a defect requires manually locating, cross-checking, and validating fragmented technical evidence before an authorized human can make a decision.**

---

## 12. Evidence and Claim Discipline

### Evidence labels

| Label | Meaning |
|---|---|
| **Brief** | Supplied by the event or enterprise problem statement |
| **Verified Context** | Supported by an authoritative or primary external source cited in the research brief |
| **Assumption** | Plausible project hypothesis that still requires enterprise or user validation |
| **Design Implication** | Product or architecture decision derived from the problem |
| **Target** | Proposed acceptance threshold, not an observed result |

### Verified context available from the research brief

- Maintenance human-factor guidance identifies fatigue and pressure as general error precursors.
- Controlled maintenance workflows require attention to applicable and current maintenance data.
- Release or certification authority remains with appropriately authorized staff.
- RAG-generated responses can still contain unsupported or contradictory claims.
- Long context and conflicting evidence remain known challenges for LLM-based systems.
- RAG is not, by itself, a security boundary against prompt injection.

### Assumptions that require partner validation

- The exact order of the partner's current defect-review workflow.
- Which roles assess, review, approve, and release each case.
- Which regulations and operator procedures apply.
- Which metadata fields are available and reliable.
- Which documents can legally be ingested and displayed.
- The frequency of incorrect references, missing fields, or source conflicts.
- Current baseline time, rework rate, and operational impact.
- Whether the selected synthetic scenario is representative.

---

## 13. Human-Authority Boundary

### The AI may

- extract and normalize defect information;
- retrieve authorized evidence;
- compare sources and revisions;
- flag missing fields, cross-references, and conflicts;
- summarize supported evidence;
- ask targeted clarification questions;
- draft a review package.

### The AI may not

- authorize dispatch;
- certify airworthiness;
- issue or sign a release to service;
- invent or silently modify a technical reference;
- mark a document approved or current;
- resolve an ungoverned source conflict;
- close or write back a maintenance record in the MVP;
- replace licensed or authorized engineering judgment.

### Required framing

> **The system accelerates evidence review. It does not make the operational decision.**

---

## 14. Judge-Relevant Fit

### Problem and track fit

- Directly addresses the supplied enterprise brief.
- Names the real users and the actual defect-review workflow.
- Explains why the failure is deeper than generic document search.

### Agentic AI fit

The problem naturally requires a bounded multi-step workflow:

```text
Understand defect
→ identify missing context
→ plan source-specific searches
→ retrieve authorized evidence
→ check applicability and revision
→ follow cross-references
→ detect conflicts
→ validate claims
→ return a review package or abstain
```

### Technical credibility bridge

The problem implies concrete controls:

- source allow-list;
- metadata filters;
- hybrid retrieval;
- applicability and revision gate;
- deterministic schema validation;
- citation support checks;
- conflict detection;
- explicit abstention;
- mandatory human review;
- reconstructable event trace.

### Impact framing

The strongest honest impact thesis is:

> **Reduce the time and cognitive load required to assemble a review-ready evidence package while improving consistency, traceability, and detection of incomplete references.**

This is a **hypothesis** until measured against a manual or single-pass RAG baseline.

---

## 15. Scoring-Oriented Quality Checklist

A strong problem-insight slide should satisfy all items below.

### User and goal

- [x] Names MCC and maintenance engineers.
- [x] States the goal: create a review-ready, source-backed defect package.
- [x] Preserves the role of the authorized human.

### Workflow failure

- [x] Shows fragmentation across document families.
- [x] Shows manual cross-referencing.
- [x] Shows that the defect entry itself may require validation.
- [x] Shows cross-document dependencies.

### Root cause

- [x] Distinguishes relevance from applicability.
- [x] Identifies revision, approval state, and effectivity as first-class checks.
- [x] Explains why search-only or chatbot-only approaches are insufficient.

### Consequence

- [x] Connects the workflow to time, rework, inconsistency, and review risk.
- [x] Avoids unsupported quantitative impact claims.
- [x] Avoids implying that engineers lack expertise.

### Solution bridge

- [x] Creates a natural reason for agentic planning and tool use.
- [x] Creates a natural reason for deterministic validation.
- [x] Creates a natural reason for abstention and human escalation.
- [x] Does not over-explain the architecture in the problem section.

### Pitch clarity

- [x] Can be explained in approximately 40 seconds.
- [x] Contains one memorable insight.
- [x] Uses plain language.
- [x] Can be retold by a non-specialist judge.

---

## 16. Instructions for an AI Agent Using This Context

When generating slides, scripts, submission text, or product requirements from this document:

1. Lead with the user and broken workflow, not the technology stack.
2. Preserve the central insight: **relevant retrieval is not sufficient evidence**.
3. Distinguish facts from assumptions and targets.
4. Do not invent partner metrics, interviews, incidents, adoption, or accuracy results.
5. Describe the product as decision support and evidence validation.
6. Keep authorized human review explicit.
7. Translate each technical capability into workflow value.
8. Prefer one concrete defect scenario over broad feature coverage.
9. Use synthetic-data disclosures whenever real enterprise data is unavailable.
10. Treat applicability, revision, provenance, conflicts, and abstention as core—not optional—controls.

### Agent output priority

When space is limited, preserve these five messages in order:

1. **One defect requires evidence across multiple technical sources.**
2. **A relevant passage may still be inapplicable or superseded.**
3. **The entered defect record itself must be validated.**
4. **Cross-references and conflicts require multi-step checking.**
5. **The AI prepares evidence; an authorized human decides.**

---

## 17. Source Documents Used

This document was synthesized from:

1. `problem_statement(2).md` — supplied enterprise problem statement, pilot scope, available data, and build direction.
2. `research-and-solution-brief(3).md` — evidence-backed problem analysis, safety boundary, workflow, pain points, risks, metrics, and product framing.
3. `AABW_Submission_Agent_Context(1).md` — judging criteria, submission strategy, evidence discipline, and requirement to lead with the problem.
4. `AABW_Pitching_Playbook_Agent_Context(2).md` — problem-insight structure, five-minute pitch guidance, and judge-facing clarity principles.

### External sources already referenced in the research brief

- FAA Human Factors in Aviation Maintenance.
- FAA AC 120-125 on MEL/CDL context.
- EASA continuing-airworthiness rules and Part-145 guidance.
- Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*.
- RAGTruth, ACL 2024.
- *Lost in the Middle*, TACL 2024.
- *Who’s Who: Large Language Models Meet Knowledge Conflicts in Practice*, EMNLP 2024.
- NIST AI Risk Management Framework and Generative AI Profile.
- OWASP guidance on prompt injection and vector/embedding weaknesses.

---

## Final Takeaway

> **The winning problem insight is not “engineers need faster document search.” It is: “engineers need a reliable way to prove that the evidence supporting a defect review is approved, current, applicable, complete, consistent, and traceable—before an authorized human decides.”**
