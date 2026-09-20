"""Module 5: Writer Agent — A2A service exposing writing capability."""

import os
from typing import Optional

import fastapi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.database import init_db
from shared.redis_client import get_redis

app = FastAPI(title="Writer Agent (A2A)", version="1.0.0")


class WritingRequest(BaseModel):
    content: str
    sources: list[str]
    tone: str = "professional"
    format: str = "article"
    target_audience: str = "general"


class WritingResponse(BaseModel):
    article: str
    word_count: int
    agent_name: str = "writer-a2a"
    capabilities: list[str] = None
    citations_formatted: bool = True

    def __init__(self, **data):
        super().__init__(capabilities=["content-generation", "style-adaptation", "citation-formatting"], **data)


class AgentCard(BaseModel):
    name: str = "writer-a2a"
    version: str = "1.0.0"
    description: str = "Writes polished articles from research findings"
    endpoint: str = "http://writer-a2a:8002/a2a"
    capabilities: list[str] = ["content-generation", "style-adaptation", "citation-formatting"]
    input_schema: dict = {
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "sources": {"type": "array"},
            "tone": {"type": "string"},
        },
        "required": ["content"],
    }
    output_schema: dict = {
        "type": "object",
        "properties": {
            "article": {"type": "string"},
            "word_count": {"type": "integer"},
            "citations_formatted": {"type": "boolean"},
        },
    }
    authentication: dict = {"type": "api_key", "header": "X-A2A-Token"}
    owner: str = "agentic-ai-course"


@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/a2a/write")
async def write(request: WritingRequest):
    """Process a writing request from the orchestrator."""
    # In production, this would call the LLM to generate the article
    # For the A2A demo, we return a structured response
    article = f"# {request.format.title()}\n\n"
    article += request.content[:500] + "\n\n"
    article += f"---\n\nSources: {', '.join(request.sources[:3])}\n"
    article += f"\nWritten in {request.tone} tone for {request.target_audience} audience."

    return WritingResponse(
        article=article,
        word_count=len(article.split()),
        citations_formatted=True,
    )


@app.post("/a2a/message")
async def handle_a2a_message(payload: dict):
    """Handle A2A protocol messages."""
    content = payload.get("content", "")
    sources = payload.get("sources", [])

    return {
        "status": "completed",
        "data": {
            "article": f"Article based on {len(sources)} sources",
            "word_count": len(content.split()),
        },
    }


@app.get("/a2a/card")
async def get_agent_card():
    """Return this agent's Agent Card."""
    return AgentCard().model_dump()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "writer-a2a"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
