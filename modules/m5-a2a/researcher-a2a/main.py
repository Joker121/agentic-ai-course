"""Module 5: Researcher Agent — A2A service exposing research capability."""

import os
from typing import Optional

import fastapi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.database import init_db
from shared.redis_client import enqueue_task, get_redis

app = FastAPI(title="Researcher Agent (A2A)", version="1.0.0")


class ResearchRequest(BaseModel):
    question: str
    max_results: int = 5
    context: Optional[str] = None


class ResearchResponse(BaseModel):
    findings: list[str]
    sources: list[str]
    confidence_score: float
    agent_name: str = "researcher-a2a"
    capabilities: list[str] = None

    def __init__(self, **data):
        super().__init__(capabilities=["web-search", "document-analysis", "source-extraction"], **data)


class AgentCard(BaseModel):
    name: str = "researcher-a2a"
    version: str = "1.0.0"
    description: str = "Researches topics and returns cited findings"
    endpoint: str = "http://researcher-a2a:8001/a2a"
    capabilities: list[str] = ["web-search", "document-analysis", "source-extraction"]
    input_schema: dict = {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
            "max_results": {"type": "integer"},
        },
        "required": ["question"],
    }
    output_schema: dict = {
        "type": "object",
        "properties": {
            "findings": {"type": "array"},
            "sources": {"type": "array"},
            "confidence_score": {"type": "number"},
        },
    }
    authentication: dict = {"type": "api_key", "header": "X-A2A-Token"}
    owner: str = "agentic-ai-course"


@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/a2a/research")
async def research(request: ResearchRequest):
    """Process a research request from the orchestrator."""
    # In production, this would call the actual research agent
    # For the A2A demo, we return a structured response
    findings = [
        f"Finding 1 about {request.question}",
        f"Finding 2 about {request.question}",
        f"Finding 3 about {request.question}",
    ]
    sources = [
        f"https://example.com/source{i}" for i in range(min(request.max_results, 3))
    ]

    return ResearchResponse(
        findings=findings,
        sources=sources,
        confidence_score=0.85,
    )


@app.post("/a2a/message")
async def handle_a2a_message(payload: dict):
    """Handle A2A protocol messages."""
    question = payload.get("question", "")
    max_results = payload.get("max_results", 5)

    return {
        "status": "completed",
        "data": {
            "findings": [f"Research finding about {question}"],
            "sources": ["https://example.com/1"],
        },
    }


@app.get("/a2a/card")
async def get_agent_card():
    """Return this agent's Agent Card."""
    return AgentCard().model_dump()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "researcher-a2a"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
