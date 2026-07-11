# Prompt — Agent Security, Governance, and Guardrails

## Copy-paste prompt

You are an enterprise AI security architect.

Design the security model for **Aircraft Maintenance Decision Copilot**.

## Threats to address

- Prompt injection in uploaded documents
- Malicious or irrelevant document content
- Cross-tenant data leakage
- Excessive tool permissions
- Secret leakage
- Unsupported recommendations
- Citation spoofing
- Obsolete document use
- Unauthorized web extraction
- Poisoned historical records
- Denial of service
- Sensitive trace exposure
- Human approval bypass

## Required controls

- Role-based access control
- Tenant isolation
- Least-privilege tool access
- Input and document validation
- Prompt-injection defense
- Trusted-source allowlist
- Retrieval provenance
- Citation verification
- Output schema validation
- Policy enforcement before tool calls
- Maximum step and cost budgets
- Audit logs
- Secret manager integration
- Redaction in traces
- Human approval gate
- Incident and rollback procedure

## Partner integration

Evaluate where the hackathon security partner, referred to in the project notes as **Antitech**, may fit. Do not invent features. Create an integration interface and mark all unverified capabilities as `TO VERIFY`.

## Deliverables

```text
docs/security.md
packages/security/policy.py
packages/security/input_guard.py
packages/security/output_guard.py
packages/security/tool_authorizer.py
packages/security/redaction.py
tests/security/
```

## Required output

Include:

- Threat model.
- Trust-boundary diagram in Mermaid.
- Risk register.
- Control matrix.
- Demo security scenario.
- Production hardening roadmap.
- Explicit statement of what the prototype does not secure.
