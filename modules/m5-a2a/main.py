"""Module 5: A2A Multi-Agent Orchestrator.

Orchestrator service that dispatches tasks to Researcher and Writer agents.
"""

import os
import json
from typing import Optional

import fastapi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.database import Base, init_db
from shared.redis_client import enqueue_task, dequeue_task, cache_message, get_redis

app = FastAPI(title="A2A Orchestrator", version="1.0.0")


# ── Data Models ───────────────────────────────────────────

class A2AMessage(BaseModel):
    """A2A protocol message."""
    message_id: str
    sender: str
    recipient: str
    type: str
    payload: dict
    timestamp: str = ""
    auth_token: Optional[str] = None


class A2AResponse(BaseModel):
    """A2A protocol response."""
    message_id: str
    status: str
    data: dict
    error: Optional[str] = None


class ResearchTask(BaseModel):
    question: str
    priority: str = "normal"
    max_results: int = 5


class WritingTask(BaseModel):
    research_content: str
    sources: list[str]
    tone: str = "professional"
    format: str = "article"


class AgentCard(BaseModel):
    """A2A Agent Card — the digital business card of an agent."""
    name: str
    version: str = "1.0.0"
    description: str
    endpoint: str
    capabilities: list[str]
    input_schema: dict
    output_schema: dict
    authentication: dict
    owner: str
    created_at: str = ""


# ── Agent Cards ───────────────────────────────────────────

ORCHESTRATOR_CARD = AgentCard(
    name="orchestrator",
    description="Dispatches research and writing tasks to specialized agents",
    endpoint="http://orchestrator:8000/a2a",
    capabilities=["task-routing", "load-balancing", "result-aggregation"],
    input_schema={
        "type": "object",
        "properties": {
            "question": {"type": "string"},
            "task_type": {"type": "string", "enum": ["research", "writing"]},
        },
    },
    output_schema={
        "type": "object",
        "properties": {"status": {"type": "string"}, "result": {"type": "dict"}},
    },
    authentication={"type": "api_key", "header": "X-A2A-Token"},
    owner="agentic-ai-course",
)

RESEARCHER_CARD = AgentCard(
    name="researcher-a2a",
    description="Researches topics and returns cited findings",
    endpoint="http://researcher-a2a:8001/a2a",
    capabilities=["web-search", "document-analysis", "source-extraction"],
    input_schema={
        "type": "object",
        "properties": {"question": {"type": "string"}, "max_results": {"type": "integer"}},
        "required": ["question"],
    },
    output_schema={
        "type": "object",
        "properties": {"findings": {"type": "array"}, "sources": {"type": "array"}},
    },
    authentication={"type": "api_key", "header": "X-A2A-Token"},
    owner="agentic-ai-course",
)

WRITER_CARD = AgentCard(
    name="writer-a2a",
    description="Writes polished articles from research findings",
    endpoint="http://writer-a2a:8002/a2a",
    capabilities=["content-generation", "style-adaptation", "citation-formatting"],
    input_schema={
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "sources": {"type": "array"},
            "tone": {"type": "string"},
        },
        "required": ["content"],
    },
    output_schema={
        "type": "object",
        "properties": {"article": {"type": "string"}, "word_count": {"type": "integer"}},
    },
    authentication={"type": "api_key", "header": "X-A2A-Token"},
    owner="agentic-ai-course",
)


# ── Orchestrator Logic ────────────────────────────────────

@app.on_event("startup")
async def startup():
    await init_db()
    redis = await get_redis()
    # Initialize queues
    await redis.ping()


@app.post("/a2a/message")
async def handle_message(message: A2AMessage):
    """Handle incoming A2A messages and route to appropriate agent."""
    if message.type == "research_request":
        task = ResearchTask(**message.payload)
        await enqueue_task("research_queue", message.payload)
        return A2AResponse(
            message_id=message.message_id,
            status="queued",
            data={"task_type": "research", "queue": "research_queue"},
        )
    elif message.type == "writing_request":
        task = WritingTask(**message.payload)
        await enqueue_task("writing_queue", message.payload)
        return A2AResponse(
            message_id=message.message_id,
            status="queued",
            data={"task_type": "writing", "queue": "writing_queue"},
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown message type: {message.type}")


@app.get("/a2a/card")
async def get_card(agent_name: str = "orchestrator"):
    """Return the Agent Card for the requested agent."""
    cards = {
        "orchestrator": ORCHESTRATOR_CARD,
        "researcher": RESEARCHER_CARD,
        "writer": WRITER_CARD,
    }
    card = cards.get(agent_name)
    if not card:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_name}")
    return card.model_dump()


@app.get("/a2a/registry")
async def registry():
    """Return all registered agent cards."""
    return {
        "agents": [
            ORCHESTRATOR_CARD.model_dump(),
            RESEARCHER_CARD.model_dump(),
            WRITER_CARD.model_dump(),
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "orchestrator"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
