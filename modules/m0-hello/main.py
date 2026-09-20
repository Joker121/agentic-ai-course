"""Module 0: Hello Agent — FastAPI health check endpoint."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(
    title="Hello Agent",
    description="Health check endpoint for Module 0 — Environment & Toolchain",
    version="0.1.0",
)


class HealthCheck(BaseModel):
    status: str
    service: str
    environment: str
    version: str


@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="healthy",
        service="hello-agent",
        environment=os.getenv("ENVIRONMENT", "development"),
        version="0.1.0",
    )


@app.get("/")
async def root():
    return {"message": "Hello Agent", "status": "running"}


@app.get("/ready")
async def ready():
    return {"ready": True, "service": "hello-agent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
