# AABW Submission and Pitching Context for an AI Agent

## Document Purpose

This document is a normalized, document-style version of the **Agentic AI Build Week 2026 Submission Playbook**. It is intended to be used as context for an AI agent that helps a hackathon team:

- evaluate whether a project fits the selected track;
- prepare submission-portal content;
- improve the project story and elevator pitch;
- verify that the project demonstrates genuine agentic behavior;
- prepare a working demo and backup demo;
- audit links, media, tools, disclosures, and required fields;
- identify missing information before submission;
- prepare a concise, credible pitch for judges.

The agent must treat the rules, deadlines, judging criteria, and submission requirements in this document as authoritative for this event context.

---

# 1. Event Context

**Event:** Agentic AI Build Week 2026  
**Location:** Ho Chi Minh City  
**Event dates:** July 8–12, 2026

The submission process is designed to assess whether a team has built a functional and credible agentic AI solution for a real enterprise problem.

A strong submission must communicate four things clearly:

1. The team understands the real problem.
2. The system performs meaningful agentic work.
3. The implementation is functional and technically credible.
4. The solution creates clear value for real users or organizations.

---

# 2. Judging Criteria

The agent should evaluate every project, draft, demo plan, and submission field against the following six criteria.

## 2.1 Agentic AI Use

The system should demonstrate more than a single prompt followed by a response.

Strong evidence includes:

- planning;
- reasoning;
- tool selection;
- tool use;
- workflow execution;
- multi-step autonomous action;
- validation of intermediate or final results;
- escalation to a human when necessary.

A project should make the agent's decisions and actions visible. If judges can only see a generated answer, they may interpret the product as a chatbot rather than an agentic system.

## 2.2 Problem and Track Fit

The project must clearly address the selected track and the actual enterprise problem statement.

The team should be able to explain:

- who experiences the problem;
- what the user is trying to achieve;
- where the existing workflow fails;
- why the problem matters;
- why the selected track is the correct fit.

Do not force a project into an unrelated track.

## 2.3 Technical Execution

The project should be functional, technically credible, and thoughtfully implemented.

Judges may look for:

- a working end-to-end workflow;
- appropriate architecture;
- reliable use of tools and external systems;
- validation and recovery mechanisms;
- permissions or human approval where appropriate;
- test cases or evaluation results;
- a demo that works under judging conditions.

## 2.4 Impact and Usefulness

The project should create clear value for real users, teams, organizations, or communities.

Useful impact measures may include:

- time saved;
- lower cost;
- fewer errors;
- faster task completion;
- improved access;
- higher consistency;
- better user satisfaction;
- reduced operational risk.

Impact claims must be supported by evidence or clearly labelled as estimates.

## 2.5 Creativity

The project should show a novel, differentiated, or original approach to the problem.

Creativity should not be presented as novelty alone. The team should explain why the approach is meaningfully better than existing workflows, a general assistant, or a simple automation.

## 2.6 Pitch and Demo Clarity

The team must communicate the problem, solution, evidence, and user value clearly within the allowed time.

Clarity is more important than covering every technical detail.

---

# 3. Core Submission Strategy

## 3.1 Build for the Actual Enterprise Brief

The project should solve the real problem statement supplied by the selected enterprise track.

Do not replace the enterprise brief with a hypothetical problem simply because it is easier to build.

## 3.2 Prefer One Project per Track

When possible, submit one project to one track.

The same project may be submitted to multiple tracks only when it genuinely fits each one. Every individual submission must still be assigned to exactly one track.

## 3.3 Lead with the Problem, Not the Technology

The submission and pitch should begin with:

1. the user;
2. the problem;
3. the workflow failure;
4. the key insight;
5. the solution.

Do not begin with the technology stack or architecture.

Architecture should support credibility, not become the main story.

## 3.4 Show Agentic Work, Not Only Output

The project should expose a visible sequence such as:

```text
USER GOAL
→ AGENT UNDERSTANDS THE OBJECTIVE
→ AGENT CREATES OR SELECTS A PLAN
→ AGENT CHOOSES TOOLS AND DATA
→ AGENT EXECUTES MULTIPLE STEPS
→ AGENT VALIDATES THE RESULT
→ AGENT RETURNS THE OUTCOME OR ESCALATES
```

The submission should state what the system:

- plans;
- decides;
- retrieves;
- calls;
- transforms;
- checks;
- executes;
- verifies;
- escalates.

## 3.5 Build a Working Demo

The exact demonstration flow should be tested before judging day.

The demo should show:

- a realistic user goal;
- the event that triggers the workflow;
- the agent's planning or decision process;
- tool use;
- meaningful actions;
- verification;
- the final user outcome.

Avoid spending demo time on login, setup, configuration, or navigation.

## 3.6 Prepare a Backup Demo

Record a backup demo video because Wi-Fi, APIs, credentials, and external systems may fail during the pitch.

The backup should show the same end-to-end workflow as the live demo.

## 3.7 Use Synthetic Data When Necessary

If real enterprise data is not available in time, plan to build with representative synthetic data.

The synthetic data should:

- reflect the structure of the expected real data;
- support the critical workflow;
- be clearly disclosed;
- avoid pretending to be real production data.

If a feature cannot be demonstrated responsibly without unavailable real data, remove or reduce that part rather than waiting indefinitely.

---

# 4. Prohibited or Weak Submission Patterns

The agent should flag the following issues.

## 4.1 Unrelated Track Selection

Do not submit to a track that the project does not genuinely address.

## 4.2 Single-Call “Agent”

A single API request wrapped in a user interface is not sufficient evidence of agentic AI.

The project should contain a meaningful decision loop, workflow, or multi-step action.

## 4.3 Technology-First Story

Do not open with model names, frameworks, databases, or cloud architecture.

Start with the problem and the user outcome.

## 4.4 Untested Live Demo

Do not wait until judging day to test the exact live flow.

Visible failures directly reduce confidence in Technical Execution.

## 4.5 Unsupported Claims

Do not invent:

- pilot results;
- user interviews;
- benchmark scores;
- time savings;
- cost savings;
- accuracy figures;
- enterprise adoption;
- production readiness;
- partner endorsements.

Clearly label an item as one of the following:

- verified result;
- observed result;
- benchmark result;
- estimate;
- assumption;
- planned future validation.

## 4.6 Incomplete Portal Fields

Do not leave required fields blank or unchecked.

The project description, team list, track, selected problem statement, tools, links, disclosures, and media must be complete and accurate.

## 4.7 Inaccurate Partner-Tool Claims

Only select technology partner tools that were genuinely used.

The submission must explain what each tool actually did.

## 4.8 Undisclosed Pre-Existing Work

Pre-existing code or assets may be used, but they must be disclosed.

---

# 5. Submission Portal Guidance

## 5.1 Team Name

The team name should be consistent with the project's branding.

It may appear on:

- the public profile;
- the project gallery;
- Demo Day materials.

## 5.2 Team Members

Add every teammate before the roster locks.

Only the team captain may be able to edit the roster afterward.

## 5.3 Track Selection

Select only the track or tracks that genuinely match the project.

The selected track determines which problem statements are available.

## 5.4 Selected Problem Statement

Choose the exact enterprise problem statement addressed by the project.

The selected problem statement is the anchor for the Problem and Track Fit score.

## 5.5 Project Title

The title should be:

- descriptive;
- memorable;
- easy to understand;
- aligned with the product's function.

Avoid titles that are clever but vague.

## 5.6 Elevator Pitch

Write one or two plain-language sentences explaining:

- who the product is for;
- what problem it solves;
- what outcome it creates;
- what distinctive agentic action it performs.

### Elevator Pitch Template

```text
[Project name] is an agentic AI system for [target user] that helps them
[desired outcome] by [planning, using tools, executing, and verifying a
distinctive workflow].
```

### Stronger Outcome-Oriented Template

```text
For [target user], [project name] reduces [specific workflow problem] by using
an AI agent to [plan], [use relevant tools or data], [take action], and
[validate or escalate the result].
```

---

# 6. Writing the “About the Project” Field

The **About the project** field is one of the most important parts of the submission.

Use the following structure.

## 6.1 Inspiration

Explain the real problem or moment that motivated the project.

Include:

- the affected user;
- the operational context;
- the workflow failure;
- why the problem matters.

Avoid generic statements such as “AI is growing quickly” or “businesses need automation.”

### Template

```text
[Target user] must [important task], but the current workflow depends on
[current limitation]. This causes [specific consequence]. We built this
project after identifying that [key insight].
```

## 6.2 What It Does

Describe the product in plain language before introducing technical details.

Explain:

- what the user provides;
- what the system does;
- what decisions the agent makes;
- what tools the agent uses;
- what outcome the user receives.

### Template

```text
The system receives [input or goal], analyzes [relevant information], creates
or selects a plan, uses [tools or systems] to execute the workflow, validates
the result against [rules, evidence, or constraints], and returns [user
outcome]. When confidence is insufficient, it [asks for approval, requests
more information, or escalates].
```

## 6.3 How It Was Built

Name the real architecture and tools used.

The explanation should connect every component to a function.

Possible categories include:

- model or models;
- agent orchestration framework;
- retrieval system;
- relational database;
- vector database;
- graph database;
- external APIs;
- browser or scraping tools;
- cloud infrastructure;
- evaluation framework;
- observability;
- security controls;
- human approval interface.

### Recommended Tool Explanation Format

| Tool or Component   | Function in the System        | Why It Was Needed               |
| ------------------- | ----------------------------- | ------------------------------- |
| `[Exact tool name]` | `[Specific action performed]` | `[Technical or product reason]` |

Do not provide a list of logos without explaining their roles.

## 6.4 Challenges Encountered

Describe what was difficult and how the team responded.

Useful challenge categories include:

- unavailable enterprise data;
- unreliable document parsing;
- tool-call failures;
- latency;
- conflicting sources;
- hallucination risk;
- evaluation design;
- permissions;
- integration complexity;
- limited build time.

### Template

```text
A major challenge was [specific challenge]. It affected [part of the workflow].
We addressed it by [implemented solution]. The remaining limitation is
[honest limitation].
```

## 6.5 Accomplishments

Choose one or more concrete achievements.

Examples:

- a complete end-to-end workflow;
- successful execution across several tools;
- a measurable benchmark;
- a robust fallback mechanism;
- a useful interface;
- an explainable evidence trail;
- a human approval loop.

Do not use unsupported superlatives such as “the best,” “revolutionary,” or “fully production-ready.”

## 6.6 Lessons Learned

State a real technical or product insight.

A useful lesson should explain how the team's understanding changed.

### Template

```text
We initially assumed [initial belief], but testing showed [observation].
As a result, we changed [design or implementation decision].
```

## 6.7 What Is Next

Explain the next validation, product, or technical steps.

Possible next steps include:

- testing with target users;
- integrating approved enterprise data;
- expanding evaluation coverage;
- improving reliability;
- implementing access controls;
- deploying a pilot;
- integrating with enterprise systems;
- measuring operational impact.

Future plans must not be presented as completed work.

## 6.8 Built With Tags

List every tool, framework, platform, database, API, and model by its exact name.

Only include tools that were actually used.

---

# 7. Links, Media, and Repository Requirements

## 7.1 Demo URL

Before submission:

- open the link in an incognito or private browser window;
- verify that authentication is not blocking judges;
- verify that required credentials are available;
- verify that the main demo workflow works;
- confirm that the application loads within a reasonable time.

## 7.2 GitHub or Repository URL

The repository should be public or accessible to judges.

The README should explain:

- what the project does;
- the architecture;
- prerequisites;
- environment variables;
- installation;
- how to run it;
- how to reproduce the demo;
- what data is synthetic;
- known limitations;
- pre-existing code or assets.

## 7.3 Image Gallery

Upload three to five screenshots showing the actual product in use.

Recommended characteristics:

- approximately 3:2 aspect ratio;
- readable text;
- visible user workflow;
- meaningful agent actions;
- visible final outcome;
- no redundant screenshots.

## 7.4 Demo Video

The submission video should be approximately two to three minutes.

It should show:

1. the user goal;
2. the workflow trigger;
3. the agent planning or deciding;
4. tool use;
5. actions;
6. verification;
7. the final outcome.

Do not submit a video that only narrates over presentation slides.

## 7.5 Partner Tools

Select every AABW technology partner tool that was genuinely used.

For each selected tool, explain:

- where it appears in the architecture;
- what data it receives;
- what operation it performs;
- what output it returns;
- how the project depends on it.

### Partner Tool Usage Template

```text
[Tool name] is used for [specific system function]. During the workflow, it
receives [input], performs [operation], and returns [output], which enables
[next agent action or user outcome].
```

---

# 8. Pitching Implications

Although this document primarily governs submission quality, the same evidence should guide the pitch.

## 8.1 Round 1 Timing

Round 1 is eight minutes total:

- five minutes for the pitch;
- two minutes for questions and answers;
- one minute for transition.

Timekeeping is strict.

## 8.2 Round 2 Timing

Round 2 is twelve minutes total.

## 8.3 Recommended Five-Minute Story

A strong pitch can follow this order:

1. Team and one-line promise.
2. Specific user and problem insight.
3. Agentic workflow.
4. Why the implementation is credible.
5. Evidence and impact.
6. Live demo.
7. Final takeaway.

## 8.4 Recommended Demo Story

```text
USER GOAL
→ WORKFLOW TRIGGER
→ AGENT PLAN
→ TOOL USE
→ AGENT ACTION
→ VALIDATION
→ USER OUTCOME
```

## 8.5 Pitch Ownership

Assign one team member to own the main narrative.

Other team members may support the demo or answer specialist questions, but frequent speaker hand-offs can reduce clarity.

## 8.6 Treat Demo Day as a Pilot Conversation

Enterprise partners may be evaluating whether the team and project are suitable for follow-up work after the event.

The pitch should therefore show:

- understanding of the enterprise workflow;
- credible implementation;
- honest limitations;
- a realistic next step;
- readiness for a pilot conversation.

---

# 9. Agent Operating Instructions

An AI agent using this document should follow these rules.

## 9.1 Preserve Accuracy

The agent must not fabricate project facts.

When information is missing, the agent should:

1. identify the missing field;
2. ask for the specific fact needed;
3. provide a placeholder only when drafting is still useful;
4. label the placeholder clearly.

## 9.2 Separate Evidence Levels

The agent should distinguish between:

- **Verified:** directly observed or measured.
- **Tested:** demonstrated in representative tests.
- **Estimated:** calculated using stated assumptions.
- **Assumed:** not yet validated.
- **Planned:** intended future work.

## 9.3 Prioritize Judge-Relevant Information

When reviewing content, prioritize:

1. genuine agentic behavior;
2. problem and track fit;
3. working technical execution;
4. user value;
5. differentiation;
6. clear communication.

## 9.4 Convert Features into Value

For every feature, the agent should ask:

```text
What does this change for the user?
```

Use the structure:

```text
Feature → Agent action → Workflow improvement → User or business outcome
```

## 9.5 Keep Technology Claims Specific

Weak:

```text
We use multiple AI technologies to optimize the workflow.
```

Strong:

```text
The retrieval component searches approved maintenance references, the agent
compares the retrieved evidence against the defect description, and the
validation step flags conflicting or missing references before an engineer
submits the case.
```

## 9.6 Flag Submission Risks

The agent should explicitly flag:

- wrong or weak track fit;
- missing project facts;
- single-call workflows described as agentic;
- unsupported impact claims;
- inaccessible links;
- untested demo flows;
- missing tool explanations;
- incomplete disclosures;
- missing human oversight;
- unlabelled synthetic data;
- missing team or portal fields;
- deadline risk.

## 9.7 Maintain Plain Language

The submission should be understandable to a judge who is not familiar with every framework or model.

Use technical detail only when it strengthens credibility.

---

# 10. Recommended Agent Outputs

## 10.1 Project Submission Draft

When asked to create a complete submission, return:

```markdown
# Project Title

## Selected Track

## Selected Problem Statement

## Elevator Pitch

## Inspiration

## What It Does

## Agentic Workflow

## How We Built It

## Challenges We Encountered

## Accomplishments

## What We Learned

## What Is Next

## Built With

## Partner Tool Usage

## Demo URL

## Repository URL

## Video Demo

## Synthetic Data Disclosure

## Pre-Existing Code or Asset Disclosure

## Known Limitations
```

## 10.2 Agentic Workflow Description

Use this format:

```markdown
| Stage            | Agent Responsibility | Tool or Data Used | Output | Validation |
| ---------------- | -------------------- | ----------------- | ------ | ---------- |
| Goal intake      | ...                  | ...               | ...    | ...        |
| Planning         | ...                  | ...               | ...    | ...        |
| Retrieval        | ...                  | ...               | ...    | ...        |
| Decision         | ...                  | ...               | ...    | ...        |
| Action           | ...                  | ...               | ...    | ...        |
| Verification     | ...                  | ...               | ...    | ...        |
| Human escalation | ...                  | ...               | ...    | ...        |
```

## 10.3 Technology Usage Table

```markdown
| Technology | Exact Role | Input | Output | Why It Matters |
| ---------- | ---------- | ----- | ------ | -------------- |
| ...        | ...        | ...   | ...    | ...            |
```

## 10.4 Evidence Table

```markdown
| Claim | Evidence Type                           | Measurement or Source | Status | Limitation |
| ----- | --------------------------------------- | --------------------- | ------ | ---------- |
| ...   | Verified / Tested / Estimated / Assumed | ...                   | ...    | ...        |
```

## 10.5 Submission Audit

```markdown
# Submission Audit

## Critical Issues

## Missing Information

## Unsupported Claims

## Agentic AI Evidence

## Track-Fit Assessment

## Technical Execution Assessment

## Impact Assessment

## Demo Readiness

## Link and Media Readiness

## Partner Tool Eligibility

## Deadline and Check-In Status

## Recommended Fixes in Priority Order
```

---

# 11. Frequently Asked Questions

## What Makes a Strong Submission?

A strong submission has:

- a clear one-line problem statement;
- a working live demo;
- visible agent planning, tool use, action, and validation;
- a credible explanation of the architecture;
- an accurate list of tools, models, and partner technologies;
- complete and correct portal fields.

## Where Is the Project Submitted?

Use the AABW event portal.

Do not use Devpost for this event.

## Can the Same Project Be Submitted to Multiple Tracks?

Yes, only when it genuinely fits each track.

Every individual submission must be associated with exactly one track.

## Is In-Person Attendance Required?

At least one team representative must check in on-site on July 12 to confirm that the team is pitching.

## Why Must Tools Be Recorded Accurately?

Technology partners may offer bonus prizes in addition to track prizes.

Eligibility depends on accurately selecting and explaining the tools actually used.

## What Should the Team Do Without Real Enterprise Data?

Use representative synthetic data, disclose it clearly, and avoid designing the entire project around data that is unlikely to arrive in time.

# 14. Bottom-Line Instruction for the Agent

Help the team produce a submission that is complete, accurate, judge-readable, technically credible, and visibly agentic.

Always prioritize:

```text
REAL PROBLEM
→ GENUINE AGENTIC WORKFLOW
→ WORKING IMPLEMENTATION
→ VERIFIED OR HONESTLY LABELLED EVIDENCE
→ CLEAR USER VALUE
→ COMPLETE SUBMISSION
```

Do not trade accuracy for persuasive language. A credible limitation is better than an unsupported claim.
