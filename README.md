# Agentic AI: From Fundamentals to Real-World A2A Applications

An instructor-led interactive video course covering the full spectrum of Agentic AI — from LLM fundamentals to production-grade multi-agent A2A systems.

## Course Structure

| Module | Title | Duration |
|--------|-------|----------|
| 0 | Environment & Toolchain | 90 min |
| 1 | LLM Fundamentals & Prompt Engineering | 90 min |
| 2 | LLM Application Primitives — Tool Calling & RAG | 90 min |
| 3 | Building an Agent from Scratch — The ReAct Loop | 90 min |
| 4 | Agent Frameworks & Patterns | 90 min |
| 5 | A2A Protocol & Multi-Agent Collaboration | 90 min |
| 6 | Production Deployment & CI/CD (FDE Execution) | 90 min |

Each module: 60 min teaching + live coding, 20 min hands-on, 10 min Q&A.

## Prerequisites

- Python 3.11+
- GitHub account
- Railway account
- LLM API key (OpenAI / Anthropic)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/<username>/agentic-ai-course.git
cd agentic-ai-course

# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your LLM_API_KEY

# Deploy to Railway
railway login
railway init
railway up
```

## Repository Structure

```
agentic-ai-course/
├── .github/workflows/deploy.yml    # CI/CD pipeline
├── modules/
│   ├── m0-hello/                   # Railway Service: hello-agent
│   ├── m2-rag/                     # Railway Service: rag-agent + Postgres
│   ├── m3-research/                # Railway Service: research-agent
│   ├── m4-framework/               # Railway Service: research-sdk + research-raw
│   └── m5-a2a/                     # Railway Services: orchestrator + researcher + writer
│       ├── agent-cards/            # Agent Card JSON files
│       ├── researcher-a2a/
│       └── writer-a2a/
├── shared/
│   ├── database.py                 # Postgres connection pool
│   ├── redis_client.py             # Redis queue
│   └── llm_provider.py             # Unified LLM invocation
├── fde/
│   ├── mva-document.md             # Minimum Viable Architecture document
│   ├── agent-cards/                # A2A business cards for all agents
│   └── value-review.md             # FDE value review record
├── tests/
├── scripts/
├── requirements.txt
├── Dockerfile
├── railway.json
└── .env.example
```

## Deployment Architecture

All modules deploy to Railway with the following services:

| Service | Source | Dependencies | Description |
|---------|--------|-------------|-------------|
| hello-agent | modules/m0-hello | None | Health check endpoint |
| rag-agent | modules/m2-rag | Postgres (pgvector), Redis | RAG chat API |
| research-agent | modules/m3-research | Postgres, Redis | Single-agent research service |
| research-sdk | modules/m4-framework | Postgres, Redis | SDK rewrite version |
| orchestrator | modules/m5-a2a | Postgres, Redis | A2A task dispatch |
| researcher-a2a | modules/m5-a2a/researcher | Postgres | A2A Agent Card exposure |
| writer-a2a | modules/m5-a2a/writer | Postgres | A2A Agent Card exposure |
| postgres | Railway template | — | Task state, agent output, vector store |
| redis | Railway template | — | Inter-agent message queue |

## FDE Methodology

Each module follows the Forward Deployed Engineering lifecycle:
**Discovery → Minimum Viable Architecture → Value Validation**

See [FDE Documents](./fde/) for MVA decisions, Agent Cards, and value reviews.

## License

MIT
