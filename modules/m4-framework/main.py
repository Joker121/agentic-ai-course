"""Module 4: Agent Frameworks — Claude Agent SDK + Raw Python comparison service."""

import os
from typing import Optional

import fastapi
from fastapi import FastAPI
from pydantic import BaseModel

from modules.m4_framework.research_sdk import ClaudeResearchAgent, ResearchResult

app = FastAPI(title="Framework Comparison Service", version="1.0.0")


class ResearchRequest(BaseModel):
    question: str
    use_sdk: bool = True


class FrameworkResponse(BaseModel):
    version: str
    lines_of_code: int
    result: Optional[ResearchResult] = None
    time_ms: int = 0


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "framework-comparison"}


@app.post("/research", response_model=FrameworkResponse)
async def research(request: ResearchRequest):
    """Run research using either the raw Python agent or the Claude SDK agent."""
    if request.use_sdk:
        agent = ClaudeResearchAgent()
        # In production, await agent.research(request.question)
        return FrameworkResponse(
            version="claude-sdk",
            lines_of_code=60,
        )
    else:
        return FrameworkResponse(
            version="raw-python",
            lines_of_code=200,
        )


@app.get("/compare")
async def compare():
    """Compare raw Python vs Claude SDK approach."""
    return {
        "raw_python": {
            "lines_of_code": 200,
            "tool_calling": "Manual parsing",
            "error_handling": "Custom",
            "deployment": "3 services",
        },
        "claude_sdk": {
            "lines_of_code": 60,
            "tool_calling": "Native function calling",
            "error_handling": "Built-in retries",
            "deployment": "1 service",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
