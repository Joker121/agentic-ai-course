# FDE Documents

This directory contains all Forward Deployed Engineering deliverables.

## Contents

| Document | Description |
|----------|-------------|
| [mva-document.md](./mva-document.md) | Minimum Viable Architecture decisions |
| [value-review.md](./value-review.md) | Per-module value validation records |
| [agent-cards/](./agent-cards/) | A2A Agent Card declarations |

## Agent Cards

Each agent service has a complete Agent Card declaration:

- **Orchestrator** — Task routing, load balancing, result aggregation
- **Researcher** — Web search, document analysis, source extraction
- **Writer** — Content generation, style adaptation, citation formatting

## Value Review Summary

All 7 modules have passed value validation. The FDE verdict is **Scale all components to production**.

Key architectural decisions:
- **pgvector** over dedicated vector store (Module 2) — saves infrastructure layer
- **Pure Python** then **Claude SDK** (Module 3-4) — teach mechanics then optimize
- **Independent Railway services** for A2A agents (Module 5) — zero context pollution
