# Product Requirements Document

> Project: Aircraft Maintenance Decision Copilot  
> Task: T02 - Define product requirements  
> Version: 0.1  
> Prepared: 11 July 2026  
> Status: Hackathon PRD for a synthetic prototype  
> Source context: [`problem_statement.md`](../problem_statement.md), [`research-and-solution-brief.md`](./research-and-solution-brief.md), and [`04_PROMPT_PRODUCT_REQUIREMENTS.md`](../hackathon_agentic_ai_prompt_pack/04_PROMPT_PRODUCT_REQUIREMENTS.md)

## Safety boundary

This product is decision support only. It does not authorize aircraft dispatch, certify airworthiness, release an aircraft to service, approve maintenance actions, or replace licensed engineering judgment. Human approval is mandatory, and in this prototype that approval means acceptance or rejection of a review package by an authorized human user. It is not an operational dispatch or release decision.

Unsupported, stale, conflicting, restricted, or weakly evidenced recommendations must be blocked or marked uncertain. All documents used by the prototype must be versioned, attributable, and clearly marked as synthetic unless an approved real source is explicitly available.

## 1. Product Vision

Aircraft maintenance teams lose time and face review risk when they must manually search, cross-reference, and validate defect evidence across AMM, MEL, CDL, TSM, engineering orders, and historical records. The Aircraft Maintenance Decision Copilot turns a defect entry into a structured, traceable evidence package that helps engineers find approved references, detect inconsistencies, and understand what still needs human review.

The hackathon product should demonstrate one polished end-to-end use case: a synthetic landing-gear indication defect where the engineer-entered record includes a current synthetic MEL reference but initially omits the linked synthetic AMM operational-check reference. The copilot retrieves current evidence, rejects a superseded distractor, detects the missing linked reference, asks for human correction, reruns validation after the edit, and prepares a cited package for authorized human review.

### Product principles

| ID | Principle | Product implication |
|---|---|---|
| PP-01 | Evidence before prose | No material claim can be shown without allowed, retrieved, versioned evidence. |
| PP-02 | Applicability before recommendation | Revision, effectivity, aircraft context, source status, and access rights are checked before synthesis. |
| PP-03 | Fail closed | Missing, contradictory, stale, restricted, or unresolved evidence blocks the package or marks it uncertain. |
| PP-04 | Human authority | The AI prepares a review package; an authorized human accepts, rejects, or requests changes. |
| PP-05 | Auditability | Every input, retrieval, validation result, citation, failure, version, and human action is reconstructable. |
| PP-06 | Synthetic-first demo | Use synthetic data unless real documents are explicitly approved for the prototype. |

## 2. Normative MVP Decisions

This PRD is the source of truth for Task T02. Where earlier planning notes mention operational states such as dispatch allowed or broad multi-source recommendations, the MVP must use the evidence-review states below.

| ID | Decision | Rationale |
|---|---|---|
| DEC-01 | The MVP supports one fixed synthetic golden path focused on landing-gear indication evidence validation. | A narrow use case is more credible for a hackathon demo and easier to evaluate. |
| DEC-02 | The system uses evidence package states, not dispatch or release states. | Prevents the prototype from implying operational authority. |
| DEC-03 | Audit trail, agent trace, and evaluation scorecard are P0 demo features. | Judges must see that the agent is controlled and measurable. |
| DEC-04 | The P0 corpus contains a current synthetic MEL, one linked synthetic AMM, and a superseded MEL distractor. | This proves targeted retrieval, cross-reference follow-up, and revision rejection. |
| DEC-05 | Human approval records review-package acceptance only. | Maintains the safety boundary while satisfying the mandatory human approval requirement. |

### Canonical state model

| State | Meaning | Allowed next states |
|---|---|---|
| `draft` | Case exists but has not entered validation. | `validating_input` |
| `validating_input` | Mandatory fields and schema are being checked. | `insufficient_information`, `retrieving_evidence` |
| `insufficient_information` | Required aircraft or defect context is missing. | `draft`, `validating_input` |
| `retrieving_evidence` | The system is retrieving allowed evidence. | `validating_evidence`, `system_unavailable` |
| `validating_evidence` | Revision, applicability, source status, cross-reference, and grounding checks are running. | `needs_human_correction`, `conflict_requires_review`, `no_supported_determination`, `ready_for_authorized_review`, `system_unavailable` |
| `needs_human_correction` | The record is inconsistent or incomplete and needs an engineer edit. | `validating_input` |
| `conflict_requires_review` | Current applicable evidence conflicts and no configured precedence rule resolves it. | `needs_human_correction`, `no_supported_determination` |
| `no_supported_determination` | Evidence is absent, weak, inaccessible, stale, or unresolved. | `draft`, `validating_input` |
| `ready_for_authorized_review` | Evidence gates passed and the package is ready for a human review action. | `evidence_package_accepted`, `evidence_package_rejected`, `needs_human_correction` |
| `evidence_package_accepted` | Authorized human accepted the evidence package for downstream workflow. This is not dispatch, release, or airworthiness approval. | Terminal for the demo case |
| `evidence_package_rejected` | Authorized human rejected the package or requested changes. | `draft`, `validating_input` |
| `system_unavailable` | A required tool, model, index, citation resolver, or audit write failed. | `retrieving_evidence`, `validating_input` |

## 3. User Personas

| ID | Persona | Goals | Pain points | Product needs |
|---|---|---|---|---|
| PER-01 | Maintenance Control Center engineer | Rapidly triage a defect, see missing context, and prepare an evidence-backed review package. | Searches across many manuals under time pressure; may miss linked references or superseded revisions. | Fast intake, targeted evidence retrieval, clear blockers, cited rationale, human review handoff. |
| PER-02 | Maintenance engineer | Validate technical references and correct defect entries before submission. | Defect records may include incomplete, mismatched, or stale references. | Reference validation, cross-reference detection, correction workflow, side-by-side evidence. |
| PER-03 | System administrator | Maintain source manifests, access controls, runtime configuration, and demo health. | Unsafe data changes can silently alter outputs. | Versioned source manifest, controlled source status changes, role policies, runtime health. |
| PER-04 | Auditor or safety reviewer | Reconstruct what happened and verify that the system stayed within authority. | Chat transcripts and ad hoc notes are difficult to audit. | Immutable timeline, evidence lineage, rejected evidence reasons, versioned evaluation results. |
| PER-05 | Authorized package reviewer | Accept, reject, or request changes for the evidence package according to assigned role. | Needs a concise but complete view without trusting unsupported AI output. | Review action gate, cited claims, uncertainty markers, rationale capture. |

## 4. Jobs To Be Done

| ID | Persona | Job to be done | Success outcome |
|---|---|---|---|
| JTBD-01 | MCC engineer | When I receive a defect entry, I want to know whether required context is present so I do not waste time reviewing an invalid record. | Missing fields are listed before retrieval and synthesis. |
| JTBD-02 | Maintenance engineer | When a reference is entered, I want to know whether it is current, applicable, and complete so I can correct it before submission. | The system validates exact source ID, revision, effectivity, and linked references. |
| JTBD-03 | Maintenance engineer | When one source points to another, I want the system to retrieve the linked source so I do not miss required context. | Targeted follow-up retrieval is visible in the trace. |
| JTBD-04 | MCC engineer | When evidence is stale, conflicting, weak, or inaccessible, I want an explicit blocker instead of a confident answer. | The package abstains or escalates with reason codes. |
| JTBD-05 | Authorized package reviewer | When I review the package, I want all material claims tied to exact citations so I can decide whether to accept, reject, or request changes. | Every claim resolves to allowed evidence with metadata and excerpts. |
| JTBD-06 | System administrator | When demo sources change, I want a controlled manifest so outputs remain reproducible. | Source versions, checksums, active/quarantined status, and access rules are tracked. |
| JTBD-07 | Auditor or safety reviewer | When I inspect a case, I want to reconstruct inputs, evidence, gates, model versions, failures, and human actions. | Timeline is complete and read-only for the auditor role. |
| JTBD-08 | Demo team | When presenting to judges, I want a short and repeatable flow that proves the agent uses tools safely. | Golden path works five consecutive times with visible trace and evaluation results. |

## 5. Functional Requirements

| ID | Priority | Requirement | Acceptance evidence |
|---|---|---|---|
| FR-01 | P0 | The system shall accept a defect description, aircraft family/type, synthetic aircraft ID, configuration/effectivity profile, operational context, suspected ATA value, and optional engineer-entered references. | Case creation form and stored input record. |
| FR-02 | P0 | The system shall preserve the original defect text separately from the normalized defect record and display normalization changes. | Original and normalized fields are visible in the report. |
| FR-03 | P0 | The system shall validate mandatory fields before retrieval and return `insufficient_information` when required context is missing. | Missing-field journey blocks evidence synthesis. |
| FR-04 | P0 | The system shall create a case ID, assessment ID, run ID, schema version, and state transition history for every assessment. | Audit timeline contains IDs and state events. |
| FR-05 | P0 | The system shall retrieve only from allow-listed sources that the current role is permitted to access. | ACL test prevents restricted evidence from appearing. |
| FR-06 | P0 | The system shall attach document metadata to every evidence item: evidence ID, document ID, title, source type, owner, revision, effective date, status, section or locator, excerpt, effectivity, synthetic flag, and checksum. | Evidence cards contain all required fields. |
| FR-07 | P0 | The system shall apply deterministic gates for approval status, revision/currentness, aircraft applicability, configuration/effectivity, and source access before evidence can support a claim. | Rejected evidence list includes reason codes. |
| FR-08 | P0 | The system shall run targeted follow-up retrieval when current applicable evidence contains a required cross-reference. | Golden path trace shows MEL-to-AMM follow-up retrieval. |
| FR-09 | P0 | The system shall validate engineer-entered references for existence, exact ID, revision, applicability, and linked-reference completeness. | Missing linked AMM reference is detected. |
| FR-10 | P0 | The system shall detect conflicting current applicable evidence and preserve both sides unless a human-configured precedence rule exists. | Conflict journey shows both evidence items and blocks automatic resolution. |
| FR-11 | P0 | The system shall classify evidence sufficiency as `sufficient`, `insufficient`, `conflicting`, or `not_evaluable`. | Report includes sufficiency classification and reason. |
| FR-12 | P0 | The system shall produce a structured analytical report containing assessment metadata, original and normalized defect, context, state, validation results, missing information, conflicts, cited evidence, rejected evidence, uncertainty reason, and required human action. | Report validates against the output schema. |
| FR-13 | P0 | The system shall require every material claim, constraint, inconsistency, and requested human action to cite at least one allowed retrieved evidence ID. | Grounding gate fails unsupported claims. |
| FR-14 | P0 | The UI shall show state, blocking issue, required human action, evidence cards, concise rationale, rejected evidence, and citation metadata without exposing private chain-of-thought. | Demo workspace presents all sections. |
| FR-15 | P0 | Only deterministic gates may transition a package to `ready_for_authorized_review`; no AI-generated operational approval state is allowed. | State enum excludes dispatch, release, and airworthiness decisions. |
| FR-16 | P0 | The system shall require active human review before completion. Only a user with reviewer permission may accept, reject, or request changes for the review package. | Unauthorized accept attempt is denied; authorized action is logged. |
| FR-17 | P0 | Every human edit shall create a new record version and rerun all required validation gates. | Correction journey shows new version and full revalidation. |
| FR-18 | P0 | The system shall implement demo roles for engineer, authorized reviewer, administrator, and auditor. | Role test verifies permissions and read/write boundaries. |
| FR-19 | P0 | The system shall save an audit trail of input, normalization, queries, retrieved evidence, rejected evidence, gates, outputs, errors, model/prompt/tool/index/corpus versions, and human events. | Audit view reconstructs the golden run. |
| FR-20 | P0 | The system shall expose agent traces for the demo: state transitions, tool calls, initial retrieval, targeted retrieval, filters, rejections, and validation outcomes. | Trace panel shows the end-to-end path. |
| FR-21 | P0 | The system shall expose an evaluation scorecard with frozen dataset version, configuration versions, numerator/denominator, pass/fail status, and run timestamp. | Evaluation panel is visible in the demo. |
| FR-22 | P0 | Retriever outage, model timeout, invalid structured output, unresolved citation, or audit write failure shall fail closed and shall not render a review-ready package. | Error journeys show safe states and retry action. |
| FR-23 | P0 | The administrator shall inspect source manifests and activate, quarantine, or retire demo sources through controlled configuration or an admin workflow. | Source status change affects new assessments only. |
| FR-24 | P0 | The auditor shall open an assessment by ID and view a read-only chronological trace, evidence lineage, validation results, and human events. | Auditor cannot mutate the case. |
| FR-25 | P0 | Every source and assessment view shall display synthetic-data labeling and a decision-support-only banner. | Banner appears in all case views and exports. |
| FR-26 | P1 | The system should export a review package that preserves citations, versions, state, human review status, and a synthetic/not-operational watermark. | Export file contains required package fields. |
| FR-27 | P2 | Historical similar-defect retrieval may be shown in a separate non-authoritative panel and must not override current applicable evidence gates. | Historical panel is visually and logically separate. |

## 6. Non-Functional Requirements

| ID | Priority | Requirement | Target or constraint |
|---|---|---|---|
| NFR-01 | P0 | Safety fail-closed behavior | False definitive recommendation rate is `0/N` on frozen safety cases. |
| NFR-02 | P0 | Citation integrity | Unsupported evidence IDs and unresolved citations are zero on the golden demo. |
| NFR-03 | P0 | Retrieval quality | All-required-evidence success@5 is at least 85 percent and context precision@5 is at least 80 percent on the frozen evaluation set. |
| NFR-04 | P0 | Structured output reliability | 100 percent of responses conform to the versioned output schema. |
| NFR-05 | P0 | Demo performance | End-to-end maximum latency is under 15 seconds across five golden runs in the declared demo environment. |
| NFR-06 | P0 | Golden-path repeatability | The golden scenario completes five consecutive times without developer intervention. |
| NFR-07 | P0 | Access control | Restricted chunk leakage is zero in role and ACL tests; agent tools are read-only. |
| NFR-08 | P0 | Prompt-injection resistance | Direct and indirect prompt-injection success is zero on the frozen adversarial set. |
| NFR-09 | P0 | Audit completeness | Every frozen run is reconstructable from an assessment ID with no missing required audit fields. |
| NFR-10 | P0 | Demo usability | The golden path can be demonstrated in under 90 seconds with state, blocker, human action, and evidence visible in one workspace. |
| NFR-11 | P0 | Authority wording | No system-generated label, button, state, or recommendation implies dispatch, release, airworthiness certification, or operational approval. |
| NFR-12 | P0 | Secret and data protection | Logs, traces, and exports contain no secrets and no source excerpt the current user is not allowed to read. |
| NFR-13 | P0 | Reproducibility | Every run records model, prompt, rule, schema, tool, index, and corpus versions. |
| NFR-14 | P0 | Source integrity | Stable evidence IDs and source checksums resolve uniquely; ambiguous current revisions fail closed or are quarantined. |

## 7. User Stories

| ID | Persona | Story | Priority |
|---|---|---|---|
| US-01 | MCC engineer | As an MCC engineer, I want to submit a defect and aircraft context so the system can create a structured case. | P0 |
| US-02 | MCC engineer | As an MCC engineer, I want missing mandatory fields called out before retrieval so I can fix the input quickly. | P0 |
| US-03 | Maintenance engineer | As a maintenance engineer, I want my entered reference checked for currentness and applicability so I can avoid stale or mismatched references. | P0 |
| US-04 | Maintenance engineer | As a maintenance engineer, I want linked references retrieved automatically so required supporting evidence is not missed. | P0 |
| US-05 | Maintenance engineer | As a maintenance engineer, I want superseded evidence shown as rejected so I understand why it was not used. | P0 |
| US-06 | MCC engineer | As an MCC engineer, I want every claim to show exact citations so I can verify the report quickly. | P0 |
| US-07 | MCC engineer | As an MCC engineer, I want the system to block uncertain or unsupported output so I am not nudged into trusting a guess. | P0 |
| US-08 | Maintenance engineer | As a maintenance engineer, I want to edit the missing reference and rerun validation so the corrected record is traceable. | P0 |
| US-09 | Authorized reviewer | As an authorized reviewer, I want to accept, reject, or request changes for the evidence package so the workflow has explicit human control. | P0 |
| US-10 | Auditor or safety reviewer | As an auditor, I want to reconstruct the complete trace so I can verify evidence, gates, failures, and human actions. | P0 |
| US-11 | System administrator | As an administrator, I want to inspect and manage the source manifest so demo evidence remains versioned and attributable. | P0 |
| US-12 | Demo team | As a demo presenter, I want an evaluation scorecard so judges see measured behavior, not only a polished answer. | P0 |
| US-13 | System administrator | As an administrator, I want restricted sources excluded by role so access control is demonstrable. | P0 |
| US-14 | Auditor or safety reviewer | As a safety reviewer, I want to confirm the interface never claims to authorize dispatch or release. | P0 |

## 8. Golden-Path User Journey

### Preconditions

| ID | Precondition |
|---|---|
| GP-PRE-01 | The corpus contains `SYN-MEL-CURRENT`, `SYN-MEL-SUPERSEDED`, and `SYN-AMM-LINKED-CHECK`. |
| GP-PRE-02 | The defect is: "Landing gear green indication is intermittent after gear extension." |
| GP-PRE-03 | Aircraft context includes synthetic family, aircraft ID, configuration/effectivity profile, phase of operation, and suspected ATA. |
| GP-PRE-04 | The initial engineer record includes `SYN-MEL-CURRENT` but omits `SYN-AMM-LINKED-CHECK`. |
| GP-PRE-05 | The demo user starts as an engineer, then an authorized reviewer performs the final review action. |

### Journey

| Step | Actor | System behavior | Resulting state |
|---|---|---|---|
| GP-01 | Engineer | Enters defect, aircraft context, and candidate synthetic MEL reference. | `validating_input` |
| GP-02 | System | Validates mandatory fields and preserves original plus normalized defect. | `retrieving_evidence` |
| GP-03 | System | Retrieves relevant synthetic MEL evidence and a superseded distractor. | `validating_evidence` |
| GP-04 | System | Rejects `SYN-MEL-SUPERSEDED` because its revision status is not current. | `validating_evidence` |
| GP-05 | System | Detects that `SYN-MEL-CURRENT` requires linked synthetic AMM evidence and runs targeted follow-up retrieval. | `validating_evidence` |
| GP-06 | System | Retrieves `SYN-AMM-LINKED-CHECK` and validates metadata, effectivity, and source status. | `validating_evidence` |
| GP-07 | System | Compares engineer-entered references with required linked evidence and finds the AMM reference missing from the record. | `needs_human_correction` |
| GP-08 | Engineer | Adds the missing `SYN-AMM-LINKED-CHECK` reference and resubmits. | `validating_input` |
| GP-09 | System | Creates a new record version, reruns all gates, binds claims to citations, and prepares the package. | `ready_for_authorized_review` |
| GP-10 | Authorized reviewer | Reviews citations and accepts the evidence package with rationale. | `evidence_package_accepted` |
| GP-11 | Auditor | Opens the case and sees input, retrievals, rejected evidence, correction, validation, evaluation, and human event. | Terminal demo view |

## 9. Error and Fallback Journeys

| ID | Scenario | Trigger | Expected fallback |
|---|---|---|---|
| EJ-01 | Missing mandatory aircraft context | Aircraft type or effectivity is blank. | Return `insufficient_information`, ask for the exact missing field, and do not retrieve or synthesize evidence. |
| EJ-02 | No current evidence found | Search returns no approved current applicable source. | Return `no_supported_determination` with abstention reason and required human action. |
| EJ-03 | Cross-reference cannot resolve | Current MEL points to a linked source not in the allowed corpus. | Block package and show unresolved cross-reference. |
| EJ-04 | Superseded evidence retrieved | Ranked retrieval includes an old revision. | Reject it with reason code and exclude it from supporting citations. |
| EJ-05 | Wrong effectivity | Evidence matches text but not aircraft/configuration. | Reject it and explain the applicability mismatch. |
| EJ-06 | Current evidence conflict | Two current applicable sources disagree and no precedence rule exists. | Set `conflict_requires_review`, show both sides, and avoid choosing a winner. |
| EJ-07 | Restricted source match | Query matches a source the user cannot access. | Hide the content from retrieval, citations, trace, and export; log ACL rejection without leaking excerpt. |
| EJ-08 | Direct prompt injection | User text asks the agent to ignore rules or reveal data. | Treat as untrusted input, keep policies unchanged, and continue only if evidence gates pass. |
| EJ-09 | Indirect prompt injection | Indexed document contains instructions to the model. | Treat retrieved text as evidence only, not as instructions. |
| EJ-10 | Retriever outage | Search service fails or times out. | Set `system_unavailable`, write failure event, and expose safe retry. |
| EJ-11 | Model timeout or invalid schema | Generation fails or returns invalid structured output. | Reject the output, log failure, and do not render a review-ready package. |
| EJ-12 | Citation resolver failure | A cited evidence ID cannot resolve to metadata and excerpt. | Fail grounding gate and block review-ready state. |
| EJ-13 | Audit persistence failure | Required audit event cannot be saved. | Fail closed because the case cannot be reconstructed. |
| EJ-14 | Human rejects package | Reviewer identifies an issue. | Store rejection or changes-requested event and return case for correction. |

## 10. Scope

### In scope for hackathon MVP

| ID | Item |
|---|---|
| SC-IN-01 | One polished synthetic use case: intermittent landing-gear green indication after gear extension. |
| SC-IN-02 | Synthetic aircraft family, tail/aircraft ID, configuration, and effectivity profile. |
| SC-IN-03 | Small curated source set: current synthetic MEL, linked synthetic AMM, superseded MEL distractor, wrong-effectivity fixture, conflict fixture, restricted fixture, and injection fixture. |
| SC-IN-04 | Typed intake, mandatory-field validation, normalization display, and record versioning. |
| SC-IN-05 | Permission-aware retrieval from an allow-listed synthetic corpus. |
| SC-IN-06 | Targeted MEL-to-AMM follow-up retrieval. |
| SC-IN-07 | Revision, applicability, source-status, citation, and cross-reference gates. |
| SC-IN-08 | Structured analytical report with citations and blocked/uncertain outcomes. |
| SC-IN-09 | Human correction and authorized package review workflow. |
| SC-IN-10 | Audit trail, agent trace, and evaluation scorecard visible in the demo. |
| SC-IN-11 | Error/fallback handling for missing fields, stale evidence, conflicts, outages, ACL, injection, and citation failures. |
| SC-IN-12 | Clear synthetic labeling and decision-support-only safety banner. |

### Out of scope for hackathon MVP

| ID | Item |
|---|---|
| SC-OUT-01 | Any claim that the system authorizes dispatch, release, airworthiness, maintenance sign-off, or operational disposition. |
| SC-OUT-02 | Use of real proprietary airline or OEM documents without explicit approval. |
| SC-OUT-03 | Automatic writeback to maintenance systems or technical logs. |
| SC-OUT-04 | Broad coverage of AMM, MEL, CDL, TSM, engineering orders, and historical logs beyond the curated demo corpus. |
| SC-OUT-05 | Production identity management, retention policy, disaster recovery, or certification. |
| SC-OUT-06 | Full knowledge graph, historical defect analytics, or multi-agent specialization unless later tasks prove value. |
| SC-OUT-07 | Numeric confidence as a safety authority or as a way to override missing/conflicting evidence. |
| SC-OUT-08 | Claims of real-world aviation performance, compliance, or regulatory approval. |

### Future work

| ID | Item |
|---|---|
| FW-01 | Add synthetic TSM and CDL scenarios after the golden path is stable. |
| FW-02 | Add non-authoritative historical similar-defect search with strict separation from approved current evidence. |
| FW-03 | Integrate with approved enterprise document repositories and maintenance systems after data governance review. |
| FW-04 | Add production-grade identity, retention, monitoring, and incident response controls. |
| FW-05 | Pilot with real maintenance teams using approved non-operational data and formal human-factors review. |

## 11. Acceptance Criteria

| ID | Priority | Given | When | Then | Traces to |
|---|---|---|---|---|---|
| AC-01 | P0 | Complete synthetic golden input | The engineer submits the case | Original text is preserved, normalized record is stored, normalization diff is visible, and validation begins. | FR-01, FR-02 |
| AC-02 | P0 | Aircraft type or effectivity is missing | The case is submitted | State is `insufficient_information`, the exact missing field is requested, and no evidence synthesis occurs. | FR-03, FR-11 |
| AC-03 | P0 | Engineer role and allow-listed sources | Initial retrieval runs | Only accessible records appear, and each evidence item has required metadata and checksum. | FR-05, FR-06 |
| AC-04 | P0 | Current and superseded synthetic MEL both match | Revision gate runs | Superseded source is rejected with reason code and excluded from supporting citations. | FR-07 |
| AC-05 | P0 | Wrong-effectivity fixture matches query text | Applicability gate runs | Evidence is rejected or marked not evaluable and cannot support review-ready state. | FR-07, FR-15 |
| AC-06 | P0 | Current MEL contains a required link to `SYN-AMM-LINKED-CHECK` | Validation runs | Targeted second retrieval is emitted and visible in the trace. | FR-08, FR-20 |
| AC-07 | P0 | The engineer record omits linked AMM reference | Completeness check runs | Blocking inconsistency appears and state becomes `needs_human_correction`. | FR-09, FR-11 |
| AC-08 | P0 | Engineer adds exact linked AMM reference | The case is resubmitted | A new record version is created, all gates rerun, prior version remains viewable, and state becomes `ready_for_authorized_review`. | FR-17, FR-19 |
| AC-09 | P0 | Output contains an evidence ID not in the allowed retrieved bundle | Grounding gate runs | Package is rejected and cannot render as review-ready. | FR-13, FR-15 |
| AC-10 | P0 | Golden report is produced | Reviewer opens each citation | Each citation resolves to document, revision, locator, excerpt, and metadata; every material claim is supported. | FR-06, FR-13, FR-14 |
| AC-11 | P0 | Two current applicable fixtures conflict | The assessment runs | Both sides are shown, state is `conflict_requires_review`, and no automatic winner is chosen. | FR-10, FR-11 |
| AC-12 | P0 | No approved current evidence exists or a cross-reference cannot resolve | Assessment runs | State is `no_supported_determination`, abstention reason is shown, and no definitive claim is made. | FR-08, FR-11 |
| AC-13 | P0 | Any success or error path in the frozen set | Output is serialized | Response validates against schema, uses allowed state enum, and includes `human_approval_required: true`. | FR-12, FR-15 |
| AC-14 | P0 | User lacks reviewer permission | User attempts to accept package | Action is denied and logged. | FR-16, FR-18 |
| AC-15 | P0 | Authorized reviewer opens review-ready package | Reviewer accepts, rejects, or requests changes | Human event stores identity, role, rationale, timestamp, and outcome; AI cannot create the event. | FR-16, FR-19 |
| AC-16 | P0 | Any assessment or source view is opened | Page renders | Synthetic label and decision-support-only banner are visible. | FR-25, NFR-11 |
| AC-17 | P0 | Completed golden run exists | Audit view opens | Timeline includes original/corrected record, both retrievals, superseded rejection, all gates, versions, and human event without chain-of-thought. | FR-19, FR-20 |
| AC-18 | P0 | Auditor role opens assessment ID | Auditor attempts mutation | Authorized timeline is visible and mutation is denied. | FR-18, FR-24 |
| AC-19 | P0 | Restricted source fixture matches query | Unauthorized role searches | Restricted content does not appear in retrieval, citation, trace, or export. | FR-05, FR-18 |
| AC-20 | P0 | Administrator quarantines a demo source | A new assessment runs | Source is not used as support; previous audit still resolves exact version used earlier. | FR-23, FR-24 |
| AC-21 | P0 | Retriever outage occurs | Assessment runs | State is `system_unavailable`, no stale or partial package is review-ready, and retry is available. | FR-22 |
| AC-22 | P0 | Model timeout, invalid JSON, or unresolved citation occurs | Policy gate runs | Package does not become review-ready and failure reason is audited. | FR-13, FR-22 |
| AC-23 | P0 | Direct or indirect prompt injection is present | Assessment runs | System rules and permissions remain unchanged and no data leak occurs. | FR-05, FR-13, FR-22 |
| AC-24 | P0 | Frozen evaluation set exists | Evaluation runs | Scorecard shows dataset/config versions, numerator/denominator, retrieval metrics, grounding failures, schema pass rate, ACL leakage, injection success, and audit completeness. | FR-21 |
| AC-25 | P0 | Frozen golden scenario | It runs five consecutive times | All five runs complete full path, reject superseded source, detect missing AMM, revalidate correction, and finish under latency target. | FR-01 through FR-25 |
| AC-26 | P0 | Teammate follows demo script | Demo is presented | Golden journey completes under 90 seconds without developer intervention. | FR-14, FR-20 |
| AC-27 | P0 | Logs and traces are scanned | Security check runs | No credentials, secrets, private chain-of-thought, or unauthorized excerpts are present. | FR-19, NFR-12 |
| AC-28 | P0 | UI labels, buttons, states, and report text are inspected | Safety wording review runs | No system-generated wording claims dispatch, release, airworthiness certification, or operational approval. | FR-15, FR-25, NFR-11 |
| AC-29 | P1 | Review package export is requested | Export runs | File preserves citations, versions, assessment state, human review status, and synthetic/not-operational watermark. | FR-26 |
| AC-30 | P2 | Historical similar-defect search is enabled | Historical result is displayed | Result appears in a non-authoritative panel and cannot override current evidence gates. | FR-27 |

## 12. Demo Data Requirements

| ID | Priority | Requirement | Notes |
|---|---|---|---|
| DDR-01 | P0 | Provide one synthetic aircraft family and one synthetic aircraft ID. | Example: `SYN-AIRCRAFT-FAMILY-A`, `SYN-TAIL-001`. |
| DDR-02 | P0 | Provide one configuration/effectivity profile for the golden path. | Example: `SYN-CFG-LG-A`. |
| DDR-03 | P0 | Provide golden defect text for intermittent landing-gear green indication after gear extension. | Used in intake and evaluation. |
| DDR-04 | P0 | Provide `SYN-MEL-CURRENT` as current applicable synthetic MEL evidence. | Must include required link to `SYN-AMM-LINKED-CHECK`. |
| DDR-05 | P0 | Provide `SYN-AMM-LINKED-CHECK` as linked current applicable synthetic AMM evidence. | Supports targeted follow-up retrieval. |
| DDR-06 | P0 | Provide `SYN-MEL-SUPERSEDED` as a superseded distractor. | Must be semantically similar enough to test revision gating. |
| DDR-07 | P0 | Provide wrong-effectivity evidence fixture. | Tests applicability rejection. |
| DDR-08 | P0 | Provide current-conflict evidence fixture. | Tests `conflict_requires_review`. |
| DDR-09 | P0 | Provide restricted-source fixture. | Tests role-based retrieval and leakage prevention. |
| DDR-10 | P0 | Provide direct and indirect prompt-injection fixtures. | Tests untrusted input handling. |
| DDR-11 | P0 | Provide source manifest metadata for every source: ID, type, title, revision, effective date, status, owner, synthetic flag, effectivity, locator, approval/provenance field, checksum, and supersession relationship. | Required for gates and citations. |
| DDR-12 | P0 | Provide frozen evaluation labels for retrieval, applicability, revision, cross-reference, conflict, grounding, ACL, injection, and audit completeness. | Required for scorecard. |
| DDR-13 | P0 | Provide demo users for engineer, authorized reviewer, administrator, and auditor. | Required for role journeys. |
| DDR-14 | P0 | Freeze corpus, prompt, model, schema, and evaluation versions before final demo recording. | Required for repeatability. |

## 13. P0/P1/P2 Backlog

| ID | Priority | Backlog item | Dependency |
|---|---|---|---|
| BL-01 | P0 | Freeze state enum, output schema, and safety wording. | T02 |
| BL-02 | P0 | Create synthetic source manifest and golden corpus. | T04, T05 |
| BL-03 | P0 | Build defect intake and mandatory-field validation. | T08, T09 |
| BL-04 | P0 | Build permission-aware retrieval over the synthetic corpus. | T05, T06 |
| BL-05 | P0 | Implement targeted MEL-to-AMM follow-up retrieval. | T06, T07 |
| BL-06 | P0 | Implement revision, applicability, source-status, and cross-reference gates. | T07, T10 |
| BL-07 | P0 | Implement claim-to-citation grounding gate. | T07, T10 |
| BL-08 | P0 | Build structured analytical report. | T07, T08 |
| BL-09 | P0 | Build UI sections for state, blocker, human action, evidence, rejected evidence, and rationale. | T09 |
| BL-10 | P0 | Build engineer correction and full revalidation workflow. | T08, T09 |
| BL-11 | P0 | Build authorized human review actions and role checks. | T08, T09, T10 |
| BL-12 | P0 | Persist reconstructable audit event timeline. | T08, T10 |
| BL-13 | P0 | Expose agent trace panel. | T07, T09, T12 |
| BL-14 | P0 | Build frozen evaluation runner and scorecard. | T11 |
| BL-15 | P0 | Add failure handling for retrieval outage, model timeout, invalid schema, unresolved citations, ACL, injection, and audit failure. | T10 |
| BL-16 | P0 | Verify five consecutive golden runs and latency target. | T11, T16 |
| BL-17 | P0 | Update README and demo script for the golden path. | T15, T16 |
| BL-18 | P1 | Add synthetic TSM fixture after golden path is stable. | T05, T06 |
| BL-19 | P1 | Add review-package export. | T08, T09 |
| BL-20 | P1 | Add admin source-management UI beyond manifest inspection. | T09 |
| BL-21 | P1 | Add hosted demo deployment. | T13 |
| BL-22 | P1 | Add provider/model abstraction notes and second-provider smoke test. | T07 |
| BL-23 | P2 | Add CDL scenario. | T05, T06 |
| BL-24 | P2 | Add non-authoritative historical similar-defect panel. | T06, T09 |
| BL-25 | P2 | Add knowledge graph links for source relationships. | T04, T06 |
| BL-26 | P2 | Integrate controlled writeback after governance approval. | Future |
| BL-27 | P2 | Pilot with approved real enterprise data. | Future |

## 14. Definition of Done

| ID | Definition |
|---|---|
| DOD-01 | The product has a complete PRD, architecture, data model, ingestion, retrieval, agent, backend, frontend, security, evaluation, and demo script aligned to this MVP scope. |
| DOD-02 | The app runs from README instructions without hidden local setup. |
| DOD-03 | The synthetic corpus and source manifest are versioned and attributable. |
| DOD-04 | The golden path completes five consecutive times without developer intervention. |
| DOD-05 | Every material report claim has a resolvable citation with metadata and excerpt. |
| DOD-06 | Unsupported, stale, conflicting, inaccessible, or weak evidence fails closed. |
| DOD-07 | Human correction and authorized package review are implemented and audited. |
| DOD-08 | No UI state, button, report, or system message claims dispatch, release, airworthiness certification, or operational approval. |
| DOD-09 | Agent trace shows state transitions, retrievals, gates, rejections, correction, and review action. |
| DOD-10 | Evaluation scorecard shows frozen dataset version, metrics, pass/fail, and timestamp. |
| DOD-11 | ACL, prompt-injection, citation failure, model failure, retriever failure, and audit failure tests are included. |
| DOD-12 | Logs and traces contain no secrets, private chain-of-thought, or unauthorized excerpts. |
| DOD-13 | The final demo can be completed under 90 seconds and a backup video exists. |
| DOD-14 | All synthetic data is clearly labeled. |
| DOD-15 | Task board and master plan link to the PRD. |
| DOD-16 | Known limitations and future work are documented honestly. |

## 15. Traceability Summary

| Product objective | Supporting requirements | Acceptance criteria |
|---|---|---|
| Accept defect and aircraft context | FR-01 through FR-04 | AC-01, AC-02 |
| Validate mandatory fields | FR-03, FR-11 | AC-02, AC-13 |
| Retrieve relevant approved or synthetic documentation | FR-05 through FR-08 | AC-03, AC-06 |
| Return citations with metadata | FR-06, FR-13, FR-14 | AC-09, AC-10 |
| Detect conflicting, obsolete, or weak evidence | FR-07, FR-10, FR-11 | AC-04, AC-05, AC-11, AC-12 |
| Produce structured analytical report | FR-12 through FR-15 | AC-10, AC-13, AC-28 |
| Require human approval | FR-16, FR-17, FR-18 | AC-14, AC-15 |
| Save audit trail | FR-19, FR-24 | AC-17, AC-18 |
| Expose trace and evaluation | FR-20, FR-21 | AC-24, AC-25, AC-26 |
| Use safe synthetic demo data | FR-25, DDR-01 through DDR-14 | AC-16, AC-27 |

## 16. Open Decisions

| ID | Decision needed | Owner | When needed |
|---|---|---|---|
| OPEN-01 | Exact role mapping between MCC engineer, maintenance engineer, certifying staff, and package reviewer. | Product and safety reviewer | Before real pilot |
| OPEN-02 | Whether any approved real documents can be used or whether demo remains fully synthetic. | Data owner and legal/security | Before ingestion |
| OPEN-03 | Final metric thresholds after the frozen evaluation set is sized. | Evaluation owner | Before demo recording |
| OPEN-04 | Production deployment, identity, retention, and audit retention requirements. | System administrator and enterprise sponsor | Post-hackathon |
| OPEN-05 | Whether P1 should prioritize TSM, CDL, historical cases, or export based on judge feedback. | Product lead | After MVP demo works |
