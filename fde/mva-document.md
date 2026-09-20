# Minimum Viable Architecture (MVA) Document

**Course:** Agentic AI: From Fundamentals to Real-World A2A Applications
**Author:** Forward Deployed Engineer
**Date:** 2025

---

## Executive Summary

This document outlines the Minimum Viable Architecture decisions made throughout the course modules, focusing on delivering working value within 30 days using Railway for deployment and GitHub for version control.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Railway Platform                      │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  API     │  │  Agent   │  │  A2A     │              │
│  │  Gateway │──│  Orchestr│──│  Runtime │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │              │                    │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐              │
│  │ Postgres │  │   Redis  │  │  Agent   │              │
│  │ (pgvector│  │  (Queue) │  │  Cards   │              │
│  │  + Cache)│  │          │  │  (JSON)  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

## Module-by-Module MVA Decisions

### Module 0: Environment & Toolchain

**Decision:** Use Python 3.11 with `uvicorn` + `FastAPI` for the minimal viable endpoint.

**Rationale:** FastAPI provides automatic OpenAPI docs, Pydantic validation, and async support with minimal configuration. Railway's Python detection works seamlessly with `requirements.txt`.

**Trade-offs:**
- ✅ Minimal setup time (< 1 hour)
- ✅ Built-in API documentation
- ❌ Not as lightweight as a plain ASGI app

### Module 2: RAG Pipeline

**Decision:** Use `pgvector` (integrated with Postgres) instead of a dedicated vector store (Pinecone, Chroma standalone).

**Rationale:**
1. **Single dependency:** Postgres is already required for conversation state. Adding pgvector adds zero new infrastructure.
2. **Cost:** pgvector is free with Railway's Postgres plan. Dedicated vector stores add cost.
3. **Simplicity:** One connection string, one pool, one backup. No cross-service synchronization.
4. **Proven value:** In under 30 days, the team can validate the RAG use case without managing a separate database.

**Trade-offs:**
- ✅ Single database to manage
- ✅ No additional cost
- ✅ ACID compliance for vector + relational data
- ❌ Less scalable than dedicated vector stores at >10M embeddings
- ❌ pgvector re-ranking is less sophisticated than dedicated services

### Module 3: Agent from Scratch

**Decision:** Pure Python implementation (~200 lines) without frameworks for the base agent.

**Rationale:**
1. **Understanding:** Building from scratch ensures the engineer understands the ReAct loop mechanics.
2. **Minimal dependencies:** No framework lock-in. Can migrate to any SDK later.
3. **Debuggability:** When the agent fails, you can trace every step.

**Trade-offs:**
- ✅ Deep understanding of agent mechanics
- ✅ No hidden framework behavior
- ❌ More manual work than using a framework

### Module 5: A2A Protocol

**Decision:** Deploy each agent (orchestrator, researcher, writer) as independent Railway services.

**Rationale:**
1. **Security boundaries:** Each agent has its own context window and dependencies.
2. **Independent scaling:** Can scale the writer agent independently of the researcher.
3. **Zero context pollution:** The orchestrator never sees the researcher's internal data.
4. **Failure isolation:** If the writer crashes, the researcher continues functioning.

**Trade-offs:**
- ✅ True separation of concerns
- ✅ Independent deployment cycles
- ❌ Network latency between services
- ❌ More complex debugging (distributed tracing needed)

## Infrastructure Decisions

| Component | Choice | Justification |
|-----------|--------|---------------|
| **Compute** | Railway Containers | Zero-config deployments, GitHub integration |
| **Database** | Postgres + pgvector | Unified relational + vector storage |
| **Cache/Queue** | Redis | Message queues, conversation caching |
| **CI/CD** | GitHub Actions | Native to repo, free for public repos |
| **LLM Provider** | OpenAI / Anthropic | Best-in-class models, simple API |
| **Version Control** | GitHub | Industry standard, CI/CD integration |

## Value Validation

### What constitutes "value" in under 30 days?

1. **Day 1-3:** Working environment with LLM API calls and streaming
2. **Day 4-7:** Deployed health check endpoint on Railway
3. **Day 8-14:** Functional RAG chatbot over personal documents
4. **Day 15-21:** Working research agent with ReAct loop
5. **Day 22-27:** A2A multi-agent collaboration
6. **Day 28-30:** Production CI/CD pipeline with automated rollback

## Conclusion

This MVA prioritizes **simplicity, speed, and proven value** over architectural perfection. The pgvector decision (Module 2) is the single most impactful architectural choice — it eliminates an entire infrastructure layer and proves the RAG concept in under a day.

---

**Next Review:** After Module 5, validate the A2A architecture against production load patterns.
