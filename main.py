from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(title="Agentic AI Course", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "agentic-ai-course"}

@app.get("/")
async def root():
    return {"message": "Agentic AI Course Platform", "status": "running", "modules": 7}

@app.get("/courses")
async def courses():
    return {"courses": [{"id": "agentic-ai-course", "title": "Agentic AI Course", "price": 499.0, "currency": "INR"}]}

@app.post("/payments/create")
async def create_payment(student_name: str = "", student_email: str = ""):
    return {"order_id": f"razor_{student_email or 'demo'}", "amount": 499.0, "currency": "INR", "status": "created"}

@app.get("/payments/create")
async def create_payment_get(student_name: str = "", student_email: str = ""):
    return {"order_id": f"razor_{student_email or 'demo'}", "amount": 499.0, "currency": "INR", "status": "created", "method": "GET"}

@app.get("/revenue/stats")
async def revenue():
    return {"total_enrollments": 0, "total_revenue": 0.0, "course_price": 499.0, "currency": "INR"}

@app.get("/modules")
async def modules():
    return {
        "modules": [
            {"id": "m0-hello", "title": "Hello World & Streaming LLM"},
            {"id": "m1-llm-fundamentals", "title": "LLM Fundamentals & Quiz CLI"},
            {"id": "m2-rag", "title": "RAG Chatbot"},
            {"id": "m3-research", "title": "ReAct Agent"},
            {"id": "m4-framework", "title": "Claude SDK Framework"},
            {"id": "m5-a2a", "title": "Multi-Agent A2A Protocol"},
            {"id": "m7-monetization", "title": "Razorpay Monetization"}
        ]
    }

@app.get("/env")
async def env_check():
    return {"PORT": os.getenv("PORT", "8000"), "LLM_API_KEY": "***" if os.getenv("LLM_API_KEY") else "not set"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
