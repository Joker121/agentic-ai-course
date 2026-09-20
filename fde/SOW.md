# Statement of Work — Agentic AI Course

## Project Overview

Forward Deployed Engineering engagement for the Agentic AI course, spanning 7 modules from environment setup to production A2A deployment.

## Scope of Work

### Phase 1: Discovery (Days 1-3)
- **Deliverable:** Environment setup, API key configuration, GitHub repo creation
- **Acceptance Criteria:** `GET /health` returns 200, `stream_llm.py` streams tokens
- **Effort:** ~8 hours
- **Cost:** $0 (Railway free tier)

### Phase 2: Solution Design (Days 4-7)
- **Deliverable:** MVA document, architectural decisions, prompt engineering toolkit
- **Acceptance Criteria:** MVA document approved, `--manifest` flag works
- **Effort:** ~16 hours
- **Cost:** $0.01 per quiz batch

### Phase 3: Solution Deployment (Days 8-21)
- **Deliverable:** All modules deployed to Railway with Postgres + Redis
- **Acceptance Criteria:** All endpoints healthy, tests passing, CI/CD pipeline functional
- **Effort:** ~40 hours
- **Cost:** ~$15/month (Postgres + Redis)

### Phase 4: Value Review (Days 22-27)
- **Deliverable:** Value review report, A2A Agent Cards, comparison analysis
- **Acceptance Criteria:** All modules validated, FDE recommendations provided
- **Effort:** ~16 hours
- **Cost:** ~$45/month (3 additional services)

### Phase 5: Decision (Days 28-30)
- **Deliverable:** Scale/Fix/Stop recommendation, production CI/CD pipeline
- **Acceptance Criteria:** GitHub Actions pipeline working, rollback tested
- **Effort:** ~8 hours
- **Cost:** CI/CD infrastructure

## Boundaries

### In Scope
- All 7 modules and their hands-on tasks
- Railway deployment for all services
- GitHub Actions CI/CD pipeline
- FDE documentation (MVA, value reviews, Agent Cards)
- Postgres + Redis infrastructure

### Out of Scope
- Custom LLM fine-tuning
- Dedicated vector store migration (beyond pgvector)
- Multi-tenant production scaling beyond basic Railway replicas
- Non-Python tool integrations
- On-premise deployment

## Key Architectural Decisions

1. **pgvector over dedicated vector store** — Saves an entire infrastructure layer
2. **Pure Python then framework** — Teaches mechanics before optimization
3. **Independent Railway services** for A2A agents — Zero context pollution

## Acceptance Criteria Summary

| Criteria | Status |
|----------|--------|
| Environment works | ✅ |
| All modules deploy to Railway | ✅ |
| Postgres + Redis operational | ✅ |
| CI/CD pipeline functional | ✅ |
| A2A Agent Cards complete | ✅ |
| FDE documentation complete | ✅ |
| Value validated per module | ✅ |
| Rollback capability tested | ✅ |
