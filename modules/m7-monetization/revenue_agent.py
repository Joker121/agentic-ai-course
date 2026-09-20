"""Module 7: Course Monetization — Revenue agent and payment processing."""

import os
from typing import Optional

import fastapi
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Revenue Agent", version="1.0.0")


class RevenueAgent:
    """Tracks course revenue, generates reports, and manages subscriptions."""

    def __init__(self):
        self.enrollments: list[dict] = []
        self.revenue_log: list[dict] = []
        self.subscriptions: list[dict] = []

    def record_enrollment(self, student_id: str, course_id: str, amount: float) -> dict:
        """Record a course enrollment."""
        record = {
            "student_id": student_id,
            "course_id": course_id,
            "amount": amount,
            "enrolled_at": os.getenv("RAZORPAY_KEY_ID", "test"),
            "status": "active",
        }
        self.enrollments.append(record)
        self.revenue_log.append(record)
        return record

    def generate_daily_report(self) -> dict:
        """Generate daily revenue summary."""
        today = os.popen("date +%Y-%m-%d").read().strip()
        total = sum(r["amount"] for r in self.revenue_log)
        return {
            "date": today,
            "total_revenue": total,
            "total_enrollments": len(self.enrollments),
            "currency": "INR",
        }

    def get_top_courses(self) -> list[dict]:
        """Get top-selling courses."""
        course_stats = {}
        for enrollment in self.enrollments:
            cid = enrollment["course_id"]
            course_stats[cid] = course_stats.get(cid, {"enrollments": 0, "revenue": 0.0})
            course_stats[cid]["enrollments"] += 1
            course_stats[cid]["revenue"] += enrollment["amount"]
        return sorted(course_stats.items(), key=lambda x: x[1]["revenue"], reverse=True)


revenue_agent = RevenueAgent()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "revenue-agent"}


@app.get("/")
async def root():
    return {"message": "Revenue Agent for Agentic AI Course"}


@app.post("/enroll")
async def enroll(student_id: str, course_id: str, amount: float = 499.0):
    """Enroll a student in a course."""
    record = revenue_agent.record_enrollment(student_id, course_id, amount)
    return {"status": "enrolled", "record": record}


@app.get("/report/daily")
async def daily_report():
    """Get daily revenue report."""
    return revenue_agent.generate_daily_report()


@app.get("/report/top-courses")
async def top_courses():
    """Get top-selling courses."""
    return {"top_courses": revenue_agent.get_top_courses()}


@app.get("/enrollments")
async def enrollments():
    """List all enrollments."""
    return {"enrollments": revenue_agent.enrollments}
