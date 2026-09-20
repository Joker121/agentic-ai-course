"""Module 7: Course Monetization — Razorpay payment integration and revenue agent."""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

import fastapi
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator

# Razorpay SDK
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    print("Warning: razorpay not installed. Install with: pip install razorpay")

app = FastAPI(title="Course Monetization Agent", version="1.0.0")


# ── Models ────────────────────────────────────────

class Course(BaseModel):
    """Course offering."""
    id: str
    title: str
    description: str
    price: float = Field(..., gt=0, description="Price in INR")
    currency: str = "INR"
    modules: int = 7
    duration_hours: int = 90
    features: list[str] = field(default_factory=list)
    created_at: str = ""


class PaymentRequest(BaseModel):
    """Request to create a payment."""
    course_id: str
    student_name: str
    student_email: str
    amount: float
    currency: str = "INR"
    notes: dict = Field(default_factory=dict)


class PaymentResponse(BaseModel):
    """Payment confirmation."""
    payment_id: str
    order_id: str
    amount: float
    currency: str
    status: str
    receipt_url: Optional[str] = None
    created_at: str


class Enrollment(BaseModel):
    """Student enrollment record."""
    student_id: str
    course_id: str
    payment_id: str
    enrolled_at: str
    status: str = "active"
    access_token: str = ""


class RevenueReport(BaseModel):
    """Revenue report."""
    total_revenue: float
    total_enrollments: int
    course_breakdown: dict
    period: str
    generated_at: str


class RazorpayConfig(BaseModel):
    """Razorpay configuration."""
    key_id: str
    key_secret: str
    is_live: bool = False
    webhook_secret: str = ""


# ── Razorpay Client ──────────────────────────────

class RazorpayClient:
    """Razorpay payment client."""

    def __init__(self, key_id: str, key_secret: str, is_live: bool = False):
        self.client = razorpay.Client(
            auth=(key_id, key_secret),
        )
        self.is_live = is_live

    def create_order(self, amount: int, currency: str = "INR", notes: dict = None) -> dict:
        """Create a Razorpay order."""
        notes = notes or {}
        order = self.client.order.create({
            "amount": int(amount * 100),  # Razorpay uses paise
            "currency": currency,
            "notes": notes,
            "payment_capture": "1",
        })
        return order

    def verify_payment(self, payment_id: str, order_id: str, signature: str) -> bool:
        """Verify a Razorpay payment signature."""
        try:
            self.client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })
            return True
        except Exception:
            return False

    def get_order(self, order_id: str) -> dict:
        """Fetch order details."""
        return self.client.order.fetch(order_id)

    def capture_payment(self, order_id: str) -> dict:
        """Capture a payment."""
        return self.client.order.capture(order_id, int(amount * 100))


# ── Revenue Agent ────────────────────────────────

@dataclass
class RevenueAgent:
    """Agent that tracks course revenue and generates reports."""

    razorpay_client: Optional[RazorpayClient] = None
    enrollments: list[Enrollment] = field(default_factory=list)
    courses: dict[str, Course] = field(default_factory=dict)

    def add_course(self, course: Course) -> None:
        """Add a course to the catalog."""
        self.courses[course.id] = course

    def process_payment(self, payment: PaymentRequest) -> PaymentResponse:
        """Process a payment and create enrollment."""
        if not self.razorpay_client:
            raise HTTPException(status_code=503, detail="Payment gateway not configured")

        course = self.courses.get(payment.course_id)
        if not course:
            raise HTTPException(status_code=404, detail=f"Course {payment.course_id} not found")

        # Create Razorpay order
        order = self.razorpay_client.create_order(
            amount=payment.amount,
            currency=payment.currency,
            notes={
                "course_id": payment.course_id,
                "student_email": payment.student_email,
                "student_name": payment.student_name,
            },
        )

        # Create enrollment record
        enrollment = Enrollment(
            student_id=f"student_{datetime.now().timestamp():.0f}",
            course_id=payment.course_id,
            payment_id=order["id"],
            enrolled_at=datetime.now().isoformat(),
            access_token=f"token_{datetime.now().timestamp():.0f}",
        )
        self.enrollments.append(enrollment)

        return PaymentResponse(
            payment_id=order["id"],
            order_id=order["order_id"],
            amount=payment.amount,
            currency=payment.currency,
            status="created",
            created_at=datetime.now().isoformat(),
        )

    def verify_webhook(self, payload: dict, signature: str) -> bool:
        """Verify Razorpay webhook signature."""
        if not self.razorpay_client:
            return False
        return self.razorpay_client.verify_payment(
            payload["razorpay_payment_id"],
            payload["razorpay_order_id"],
            signature,
        )

    def generate_report(self, period: str = "monthly") -> RevenueReport:
        """Generate revenue report."""
        total_revenue = sum(
            self.courses[c.course_id].price
            for c in self.enrollments if c.status == "active"
        )
        total_enrollments = len(self.enrollments)

        course_breakdown = {}
        for enrollment in self.enrollments:
            course_id = enrollment.course_id
            if course_id not in course_breakdown:
                course_breakdown[course_id] = {"enrollments": 0, "revenue": 0.0}
            course_breakdown[course_id]["enrollments"] += 1
            course_breakdown[course_id]["revenue"] += self.courses[course_id].price

        return RevenueReport(
            total_revenue=total_revenue,
            total_enrollments=total_enrollments,
            course_breakdown=course_breakdown,
            period=period,
            generated_at=datetime.now().isoformat(),
        )


# ── API Endpoints ─────────────────────────────────

revenue_agent = RevenueAgent()


@app.on_event("startup")
async def startup():
    """Initialize the monetization agent."""
    key_id = os.getenv("RAZORPAY_KEY_ID", "")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
    if key_id and key_secret:
        revenue_agent.razorpay_client = RazorpayClient(key_id, key_secret)
        revenue_agent.add_course(Course(
            id="agentic-ai-course",
            title="Agentic AI: From Fundamentals to Real-World A2A Applications",
            description="7-module instructor-led course covering LLM fundamentals, RAG, ReAct agents, frameworks, and A2A protocol",
            price=499.0,
            modules=7,
            duration_hours=90,
            features=[
                "Full course video content",
                "6 GitHub repositories with production code",
                "Railway deployment for all services",
                "CI/CD pipeline with automated rollback",
                "FDE documentation and Agent Cards",
                "Postgres + Redis infrastructure",
                "Lifetime access and updates",
            ],
            created_at=datetime.now().isoformat(),
        ))


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "monetization-agent"}


@app.get("/")
async def root():
    return {"message": "Course Monetization Agent", "status": "running"}


@app.get("/courses")
async def list_courses():
    """List available courses."""
    return {"courses": list(revenue_agent.courses.values())}


@app.get("/courses/{course_id}")
async def get_course(course_id: str):
    """Get course details."""
    course = revenue_agent.courses.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@app.post("/payments/create")
async def create_payment(payment: PaymentRequest):
    """Create a payment order."""
    try:
        result = revenue_agent.process_payment(payment)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/razorpay")
async def razorpay_webhook(payload: dict):
    """Handle Razorpay webhook events."""
    event = payload.get("event")
    if event == "payment.captured":
        payment_id = payload["payload"]["payment"]["entity"]["id"]
        # Update enrollment status
        for enrollment in revenue_agent.enrollments:
            if enrollment.payment_id == payment_id:
                enrollment.status = "active"
                enrollment.access_token = f"token_{datetime.now().timestamp():.0f}"
        return {"status": "ok"}
    return {"status": "ignored"}


@app.get("/revenue/report")
async def revenue_report(period: str = Query("monthly", enum=["daily", "weekly", "monthly", "all"])):
    """Generate revenue report."""
    if not revenue_agent.razorpay_client:
        raise HTTPException(status_code=503, detail="Payment gateway not configured")
    return revenue_agent.generate_report(period)


@app.get("/enrollments")
async def list_enrollments():
    """List all enrollments."""
    return {"enrollments": revenue_agent.enrollments}


@app.get("/stats")
async def stats():
    """Course statistics."""
    return {
        "total_enrollments": len(revenue_agent.enrollments),
        "total_courses": len(revenue_agent.courses),
        "active_course": "agentic-ai-course",
        "price": 499.0,
        "currency": "INR",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
