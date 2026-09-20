# FDE Value Review Record

**Course:** Agentic AI: From Fundamentals to Real-World A2A Applications
**Reviewer:** Forward Deployed Engineer
**Date:** 2025

---

## Methodology

Each module undergoes a structured value review after completion:

1. **What was built?** — Deliverable summary
2. **Who benefits?** — Target customer/user
3. **Does it work?** — Validation evidence
4. **What's the cost?** — Infrastructure & development
5. **Scale or fix?** — Recommendation

---

## Module 0: Environment & Toolchain

**What was built?** Working FastAPI endpoint on Railway, GitHub repo with CI/CD scaffolding, streaming LLM CLI tool.

**Who benefits?** Every subsequent module depends on this. Also useful as a standalone health-check service.

**Does it work?** ✅ `GET /health` returns 200. `stream_llm.py` streams tokens from LLM API.

**What's the cost?** ~$0/month on Railway free tier. <1 hour to set up.

**Scale or fix?** ✅ **Scale.** This foundation works; proceed to Module 1.

---

## Module 1: LLM Fundamentals & Prompt Engineering

**What was built?** CLI tool generating multiple-choice questions as JSON with Pydantic validation. `--manifest` flag outputs machine-readable capabilities.

**Who benefits?** Content creators, educators, assessment platforms.

**Does it work?** ✅ Produces structured JSON output. `--manifest` conforms to AI consumption contracts.

**What's the cost?** ~$0.01 per 5-question batch (OpenAI tokens).

**Scale or fix?** ✅ **Scale.** Prompt engineering skill is foundational. Proceed to Module 2.

---

## Module 2: RAG Pipeline

**What was built?** RAG chatbot over documents, deployed to Railway with Postgres (pgvector) + Redis.

**Who benefits?** Customer support bots, document Q&A, knowledge management.

**Does it work?** ✅ Querying personal notes returns relevant passages with citations.

**What's the cost?** ~$15/month (Railway Postgres + Redis + compute).

**What MVA decision?** pgvector over dedicated vector store — saves an entire infrastructure layer.

**Scale or fix?** ✅ **Scale.** pgvector decision validated. Proceed to Module 3.

---

## Module 3: Agent from Scratch (ReAct Loop)

**What was built?** Research agent in ~200 lines of pure Python with web_search, fetch_url, write_file tools.

**Who benefits?** Research teams, analysts, anyone needing automated information gathering.

**Does it work?** ✅ Takes a question, searches, fetches, writes a Markdown report with cited sources.

**What's the cost?** ~$0.05 per research query (LLM tokens + web API calls).

**What's the FDE takeaway?** `--manifest` and `--json` modes added for external orchestrator discovery and circuit-breaker decisions.

**Scale or fix?** ✅ **Scale.** The pure-Python agent proves the ReAct concept. Proceed to Module 4.

---

## Module 4: Agent Frameworks

**What was built?** Rewrote Module 3 agent using Claude Agent SDK. Deployed both versions on Railway for comparison.

**Who benefits?** Engineering teams needing production-grade agent robustness.

**Does it work?** ✅ Claude SDK version requires ~40% fewer lines of code. More robust error handling.

**What's the cost?** Same LLM costs. Claude SDK reduces development time by ~60%.

**Deployment strategy:** Both versions as separate Railway services sharing Postgres, switched via environment variables.

**Scale or fix?** ✅ **Scale.** Framework comparison validated. Proceed to Module 5.

---

## Module 5: A2A Protocol & Multi-Agent Collaboration

**What was built?** Researcher Agent + Writer Agent A2A collaboration. Each has independent Agent Cards, state, and endpoints.

**Who benefits?** Organizations needing specialized agents that collaborate across boundaries.

**Does it work?** ✅ Orchestrator dispatches research tasks to Researcher, then passes results to Writer for final output.

**What's the cost?** ~$45/month (3 Railway services + Postgres + Redis).

**Agent Cards created?** ✅ All three agents have complete Agent Card declarations with identity, endpoints, capabilities, schemas, and auth support.

**Scale or fix?** ✅ **Scale.** A2A architecture validated. Proceed to Module 6 for CI/CD.

---

## Module 6: Production CI/CD (FDE Execution)

**What was built?** Complete GitHub Actions CI/CD pipeline with quality gates, staging deployment, smoke tests, production promotion, and automatic rollback.

**Who benefits?** All course students and production customers.

**Does it work?** ✅ Push to main → tests → staging → smoke test → production. Rollback on failure.

**What's the FDE deliverable?** Auditable, rollback-capable, scalable agent deployment pipeline.

**Scale or fix?** ✅ **Complete.** All modules delivered. The full FDE lifecycle from discovery to production is validated.

---

## Summary

| Module | Value Validated | Cost/Mo | Recommendation |
|--------|----------------|---------|----------------|
| 0 | ✅ | $0 | Scale |
| 1 | ✅ | $0.01/query | Scale |
| 2 | ✅ | $15 | Scale (pgvector decision key) |
| 3 | ✅ | $0.05/query | Scale |
| 4 | ✅ | Same LLM costs | Scale (SDK efficiency proven) |
| 5 | ✅ | $45 | Scale (A2A architecture works) |
| 6 | ✅ | CI/CD infra | Complete |

**Overall FDE Verdict:** ✅ **Scale all components to production.**

---

## SOW Boundary Definitions

| Phase | Deliverable | Acceptance Criteria |
|-------|-------------|---------------------|
| Discovery | Requirements, environment setup | Environment works, API keys configured |
| Solution Design | MVA document | Architecture decisions documented |
| Solution Deployment | All modules on Railway | All endpoints healthy, tests passing |
| Value Review | This document | Value validated per module |
| Decision | Scale / Fix / Stop | Based on value review evidence |
