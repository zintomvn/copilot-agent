# AABW Pitching Playbook — Agent Context Document

## 1. Purpose

This document is a practical operating guide for creating, reviewing, and improving a **five-minute Round 1 pitch** at Agentic AI Build Week (AABW).

The pitch has one primary job: help judges quickly understand the problem, see the agent perform meaningful work, believe the proposed outcome, and trust the team’s execution.

The governing principle is:

> **Clarity beats coverage.**

A strong pitch does not attempt to explain every feature or every component. It presents the smallest set of facts, evidence, and demonstrations needed for judges to understand and score the project confidently.

---

## 2. Judging Framework

The pitch should be designed around the six criteria below.

| Criterion | Question the pitch must answer |
| --- | --- |
| **Agentic AI use** | Does the system plan, reason, select tools, take action, and verify its work? |
| **Problem / track fit** | Does the team understand the real user, workflow, and enterprise problem behind the selected track? |
| **Technical execution** | Is the workflow functional, credible, controlled, and thoughtfully implemented? |
| **Impact / usefulness** | What becomes measurably better for users, teams, organizations, or communities? |
| **Creativity** | Why is this approach meaningfully different from existing alternatives or a general-purpose assistant? |
| **Pitch / demo clarity** | Can judges follow the story, remember the value, and understand the result within the time limit? |

Every pitch section should contribute to at least one criterion. Content that does not improve judge understanding or confidence should be removed.

---

## 3. Core Pitch Principles

### 3.1 Start with the problem, not the technology

Open with the target user, the goal they are trying to achieve, and the specific failure in the current workflow. Do not begin with architecture, frameworks, model names, or a list of integrations.

### 3.2 Present insight, not a repetition of the brief

The team should show what it learned about the problem. Use language such as:

> “We discovered that…”

A useful problem explanation contains:

- **Who:** the specific user or stakeholder.
- **Goal:** what that user needs to accomplish.
- **Friction:** where the workflow becomes slow, unreliable, expensive, or risky.
- **Root cause:** why current tools or processes do not solve the problem.
- **Evidence:** what the team observed, tested, measured, or validated.

One concrete insight is more persuasive than several generic statistics.

### 3.3 Make agentic behavior visible

Judges should be able to see that the system performs a multi-step workflow rather than wrapping a single model response.

Use the following structure:

```text
GOAL → PLAN → TOOLS → ACT → VERIFY
```

- **Goal:** understand the user’s objective and constraints.
- **Plan:** break the objective into executable steps.
- **Tools:** select the relevant data sources, APIs, systems, or specialist agents.
- **Act:** execute tasks and update the workflow state.
- **Verify:** check results, recover from failure, request approval, or escalate uncertainty.

When decisions, tool calls, and verification are invisible, the product may appear to be only a chatbot.

### 3.4 Translate features into user value

Do not stop at describing a feature. Explain why the feature matters.

| Feature | User value |
| --- | --- |
| Multiple agents | Specialists divide, cross-check, and validate different parts of the workflow. |
| API integrations | The task is completed across tools the user already relies on. |
| Automated reports | Scattered information becomes a decision-ready output in minutes. |
| Human approval | High-risk actions remain controlled and accountable. |
| Retrieval and citations | Recommendations can be traced to supporting evidence. |

For every important feature, complete the sentence:

> **“This matters because…”**

### 3.5 Use architecture as evidence

Architecture supports credibility, but it is not the main character of the pitch. Show only the technical choices that help prove the system is real, reliable, controlled, and evaluated.

---

## 4. Five-Minute Pitch Structure

The team should rehearse the pitch to approximately **4 minutes 45 seconds**, leaving 15 seconds of safety.

| Time | Section | Purpose |
| ---: | --- | --- |
| **0:00–0:40** | Identity and promise | Establish the team, project, target user, and core outcome. |
| **0:40–1:20** | Problem insight | Explain the user, workflow failure, root cause, and evidence. |
| **1:20–2:20** | Agentic solution | Show how the agent plans, uses tools, acts, and verifies. |
| **2:20–3:05** | Technical credibility | Prove the workflow is functional, reliable, controlled, and evaluated. |
| **3:05–3:50** | Evidence and impact | Present the strongest validated result available. |
| **3:50–4:50** | Demo | Show the agent producing a meaningful user outcome. |
| **4:50–5:00** | Close | Reinforce one memorable takeaway. |

### 4.1 Identity and promise: 0:00–0:40

State the team and project immediately.

```text
We are [TEAM].
We built [PROJECT] for [TRACK / TARGET USER].
```

Use a promise statement:

> For **[target user]**, we deliver **[valuable outcome]** by using an AI agent to **[distinctive action]**.

A short credibility line may follow:

> Domain expertise × AI engineering × product execution.

The opening should communicate relevance and value before technical detail.

### 4.2 Problem insight: 0:40–1:20

Describe one representative user and one important workflow. Explain where it breaks and why existing options are insufficient.

Recommended structure:

```text
[USER] needs to [GOAL].
Today, the process fails at [FRICTION].
The underlying cause is [ROOT CAUSE].
We discovered / observed / measured [EVIDENCE].
```

Avoid copying the problem statement verbatim. Demonstrate that the team understands the operating reality behind it.

### 4.3 Agentic solution: 1:20–2:20

Explain the workflow from user goal to verified action.

```text
The user provides [GOAL / INPUT].
The agent creates a plan by [PLANNING BEHAVIOR].
It uses [TOOLS / DATA / SYSTEMS] to [ACTIONS].
It verifies the result through [CHECKS / APPROVAL / ESCALATION].
The user receives [OUTCOME].
```

The explanation should clearly identify:

- decisions made by the system;
- tools selected or called;
- actions executed;
- state passed between steps or agents;
- validation, recovery, or human oversight.

### 4.4 Technical credibility: 2:20–3:05

Show only the implementation details that build confidence.

| Credibility principle | Evidence to present |
| --- | --- |
| **Real** | A functional end-to-end workflow rather than disconnected mock screens. |
| **Reliable** | Validation, retry, recovery, fallback, or escalation behavior. |
| **Controlled** | Permissions, human approval, guardrails, or restricted actions. |
| **Evaluated** | Representative test cases, benchmarks, user tests, or pilot results. |

Good technical evidence may include:

- a concise workflow diagram;
- one critical tool integration;
- a validation or approval step;
- an evaluation result;
- a fallback path when an API, model, or data source fails.

Do not turn this section into a tutorial about the entire stack.

### 4.5 Evidence and impact: 3:05–3:50

Use the strongest evidence the team actually has. Never present an assumption as a measured result.

Evidence hierarchy:

1. **Pilot results:** measured with target users in a realistic workflow.
2. **User tests:** observed tasks and structured feedback.
3. **Benchmarks:** representative scenarios evaluated consistently.
4. **Assumptions:** estimated outcomes, clearly labelled as assumptions.

Possible impact dimensions include:

- time saved;
- cost reduced;
- errors prevented;
- completion rate improved;
- access expanded;
- user satisfaction increased;
- decision quality or consistency improved.

A useful impact statement follows this pattern:

```text
In [TEST / SAMPLE / SCENARIO], the system changed [BASELINE METRIC]
from [BEFORE] to [AFTER], representing [IMPROVEMENT].
```

When results are not yet available, say what has been validated, what remains uncertain, and how it will be tested.

### 4.6 Demo: 3:50–4:50

The demo should tell a complete story in one minute.

| Demo time | Stage | What to show |
| ---: | --- | --- |
| **0–10s** | Goal | The task the user needs completed. |
| **10–20s** | Trigger | The input or event that starts the workflow. |
| **20–45s** | Agent acts | Planning, tool use, decisions, and verification. |
| **45–55s** | Outcome | The result delivered to the user. |
| **55–60s** | Proof | One memorable metric, citation, validation, or saved action. |

Skip login screens, setup, navigation, and decorative interactions. Start as close as possible to the meaningful task and end on the user outcome.

Prepare a backup recording of the exact demo flow in case of connectivity, authentication, or API failure.

### 4.7 Close: 4:50–5:00

End with one clear sentence that connects the project, user, and outcome.

> With **[project]**, **[target user]** can **[valuable outcome]** through an agent that **[distinctive capability]**.

The close should be a takeaway, not a new feature or new claim.

---

## 5. Recommended Main Deck

A six-slide deck is sufficient for the complete story:

1. **Team and promise**
2. **Problem insight**
3. **Agentic workflow**
4. **Why the solution wins**
5. **Evidence and impact**
6. **Demo and close**

The deck supports the speaker. It should not compete with the speaker through dense text, excessive diagrams, or unnecessary technical detail.

---

## 6. Q&A Strategy

Round 1 includes a short Q&A period. The team should use answers that are direct, supported, and honest.

A useful answer structure is:

1. **Answer:** lead with the conclusion.
2. **Support:** provide one fact, example, test, or design choice.
3. **Connect:** return to user value or risk reduction.

Target approximately **15–25 seconds per answer**.

When appropriate, collect the judges’ questions before answering:

```text
NOTE → GROUP → ANSWER IN ORDER
```

When the team does not know the answer, it should state:

- what has not yet been validated;
- what is currently known;
- how the uncertainty will be tested or reduced.

Do not fabricate results, customers, integrations, security controls, or production readiness.

### Questions that commonly test credibility

| Area | Questions to prepare for |
| --- | --- |
| **Agent** | Why does this require an agent? What decisions does it make? What tools does it use? |
| **Problem** | Who validated the problem? What alternatives exist? Why are they insufficient? |
| **Technology** | What is functional now? What fails? How is data protected? What happens when the model is wrong? |
| **Impact** | Where do the numbers come from? Who tested the system? What is the baseline? |
| **Differentiation** | Why cannot a general-purpose assistant perform the same workflow? |

---

## 7. Supporting Evidence and Appendix

Prepare appendix material before judges ask for it. Useful appendix sections include:

- **A1 — Agentic workflow**
- **A2 — Technical architecture**
- **A3 — Safety and human oversight**
- **A4 — User research**
- **A5 — Impact or ROI calculation**
- **A6 — Alternatives and differentiation**
- **A7 — Evaluation results**
- **A8 — Roadmap and limitations**

Answer the question verbally first. Show an appendix page only as supporting evidence.

---

## 8. Six Questions Every Pitch Must Answer

Before finalizing the pitch, ensure it answers all six questions:

1. **Agentic AI:** What does the system plan, decide, use, execute, and verify?
2. **Track fit:** Who has the problem, and what did the team learn about it?
3. **Execution:** What proves the workflow is functional and credible?
4. **Impact:** What becomes measurably better?
5. **Creativity:** Why is this approach meaningfully different?
6. **Clarity:** Can judges accurately retell the problem, solution, and outcome afterward?

---

## 9. Reusable Five-Minute Script Template

### 0:00 — Team, project, and promise

```text
We are [TEAM]. We built [PROJECT] for [TRACK / USER].
For [TARGET USER], we deliver [VALUABLE OUTCOME] by using an AI agent to [DISTINCTIVE ACTION].
```

### 0:40 — Problem insight

```text
[USER] needs to [GOAL], but the workflow breaks at [FRICTION].
Current options fail because [ROOT CAUSE].
We discovered [EVIDENCE / INSIGHT].
```

### 1:20 — Agentic workflow

```text
Our agent understands [GOAL], creates a plan to [PLAN],
uses [TOOLS] to [ACTIONS], and verifies the result through [CHECKS / APPROVAL].
The user receives [OUTCOME].
```

### 2:20 — Credibility and differentiation

```text
The workflow is functional end to end.
We make it reliable through [VALIDATION / RECOVERY],
controlled through [PERMISSIONS / HUMAN OVERSIGHT],
and evaluated using [TEST METHOD].
Unlike [ALTERNATIVE], we [DIFFERENTIATOR].
```

### 3:05 — Evidence and impact

```text
In [TEST / SCENARIO], we observed [RESULT].
This changes [METRIC] from [BEFORE] to [AFTER].
[If estimated: This is an assumption that we will validate through ...]
```

### 3:50 — Demo

```text
Here is the user’s goal.
This event triggers the workflow.
The agent plans, calls tools, takes action, and checks its result.
The user receives this outcome.
The proof is [METRIC / CITATION / COMPLETED ACTION].
```

### 4:50 — Close

```text
With [PROJECT], [USER] can [OUTCOME] through an agent that [DISTINCTIVE CAPABILITY].
```

---

## 10. Final Rehearsal Checklist

- [ ] Team name, project name, and track are visible and consistent.
- [ ] The opening states the user and valuable outcome.
- [ ] The problem includes a specific insight or evidence.
- [ ] The agent’s planning, decisions, tool use, actions, and verification are explicit.
- [ ] Features are translated into user value.
- [ ] Technical claims match what is actually functional.
- [ ] Reliability, control, and recovery are addressed.
- [ ] Impact is measured or clearly labelled as an assumption.
- [ ] The demo is no longer than 60 seconds.
- [ ] The demo skips setup and ends on the outcome.
- [ ] A backup demo recording is ready.
- [ ] The full pitch finishes by approximately 4:45.
- [ ] Appendix pages are numbered and easy to access.
- [ ] Q&A owners are assigned.
- [ ] Hard questions have been rehearsed.

---

## 11. Instructions for an AI Pitching Agent

When this document is used as context for an AI agent, the agent should follow these rules.

### 11.1 When generating a pitch

The agent must:

- identify the target user, goal, friction, root cause, and evidence;
- explicitly describe the agentic loop: goal, plan, tools, action, and verification;
- connect every major feature to user value;
- separate validated results from estimates or assumptions;
- produce content that can be delivered within five minutes;
- reserve approximately one minute for the demo;
- end with one memorable outcome statement;
- avoid unsupported claims and invented evidence.

### 11.2 When reviewing a pitch

The agent should score or critique the pitch against all six judging criteria. For each criterion, it should provide:

1. the current evidence in the pitch;
2. the main weakness or missing information;
3. one concrete revision;
4. the expected effect on judge understanding or confidence.

The agent should prioritize revisions in this order:

1. unclear problem or track fit;
2. invisible agentic behavior;
3. non-functional or unsupported technical claims;
4. missing evidence or impact;
5. weak differentiation;
6. excessive detail or poor timing.

### 11.3 When information is missing

The agent must not invent user research, metrics, pilot results, customers, partnerships, security guarantees, or production capabilities.

It should use explicit placeholders such as:

- `[NEEDS USER EVIDENCE]`
- `[NEEDS BASELINE METRIC]`
- `[ASSUMPTION — NOT VALIDATED]`
- `[DEMO STEP NOT IMPLEMENTED]`
- `[TECHNICAL CLAIM TO VERIFY]`

It may then recommend the fastest way to obtain or validate the missing information.

### 11.4 Preferred output format

For a complete pitch-generation request, the agent should return:

1. **One-line problem statement**
2. **One-line promise statement**
3. **Five-minute script with timestamps**
4. **Six-slide content outline**
5. **One-minute demo storyline**
6. **Evidence and assumptions table**
7. **Likely judge questions and suggested answers**
8. **Final timing and credibility checklist**

---

## 12. Bottom Line

A high-scoring AABW pitch makes the problem specific, the agentic workflow visible, the technical claims credible, and the impact measurable. It demonstrates the product through a concise outcome-focused demo and communicates only what judges need in order to understand, believe, and score the project.
