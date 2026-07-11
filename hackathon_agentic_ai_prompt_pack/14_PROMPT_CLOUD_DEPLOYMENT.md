# Prompt — AWS Cloud Deployment

## Copy-paste prompt

You are a senior cloud and DevOps engineer.

Create a minimal, secure, reproducible AWS deployment for **Aircraft Maintenance Decision Copilot**.

## Hackathon goal

Deploy the frontend, API, PostgreSQL, vector storage, Neo4j, and observability components with the smallest reasonable operational burden.

## Preferred deployment options

Evaluate two approaches:

### Option A — Fast hackathon deployment

- One AWS VM
- Docker Compose
- Reverse proxy
- Managed DNS or temporary public endpoint
- Restricted inbound ports

### Option B — Production evolution

- Managed database
- Managed container service
- Private networking
- Secret manager
- Load balancer
- Autoscaling
- Centralized logging

## Required tasks

1. Create Dockerfiles.
2. Create `docker-compose.yml`.
3. Define environment variables.
4. Create deployment scripts.
5. Add health checks.
6. Configure HTTPS path or document the limitation.
7. Configure firewall and least-privilege access.
8. Add backup and restore notes.
9. Add cost-control notes.
10. Add shutdown instructions to avoid unnecessary charges.

## Deliverables

```text
docker-compose.yml
infra/aws/
scripts/deploy.sh
scripts/stop.sh
docs/deployment.md
.env.example
```

## Constraints

- Never commit cloud credentials.
- Do not expose PostgreSQL, Neo4j, Qdrant, Prometheus, or Grafana publicly unless protected.
- Use security groups and private networking where practical.
- The demo must have a local fallback.
- Clearly separate verified AWS free credits from assumptions.
- Do not claim a service is free without checking the current account and pricing terms.
