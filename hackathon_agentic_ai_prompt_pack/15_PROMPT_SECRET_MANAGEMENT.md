# Prompt — Secrets, Configuration, and Repository Hygiene

## Copy-paste prompt

You are a security-focused DevOps engineer.

Create a complete secret-management and configuration plan for **Aircraft Maintenance Decision Copilot**.

## Secrets may include

- OpenAI API key
- AWS credentials
- Supabase or PostgreSQL credentials
- Neo4j credentials
- Qdrant API key
- LangSmith API key
- Langfuse keys
- Tinyfish key
- Security partner credentials
- Session signing keys

## Required tasks

- Create `.env.example`.
- Add `.env`, key files, credentials, logs, and local databases to `.gitignore`.
- Validate required environment variables at startup.
- Redact secrets from logs and traces.
- Separate local, demo, and production configurations.
- Document AWS Secrets Manager or equivalent for production.
- Add a pre-commit secret scan.
- Add a GitHub Actions secret scan.
- Create a key rotation checklist.
- Create an incident response checklist for an exposed key.

## Deliverables

```text
.env.example
.gitignore
.pre-commit-config.yaml
.github/workflows/secret-scan.yml
docs/secrets.md
packages/security/redaction.py
```

## Acceptance criteria

- The application fails clearly when a required secret is missing.
- No secret value appears in logs.
- The repository can be made public safely after running the documented checks.
