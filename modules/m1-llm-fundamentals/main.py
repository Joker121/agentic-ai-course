"""Module 1: LLM Fundamentals & Prompt Engineering.

CLI tool that takes a topic and outputs 5 multiple-choice questions as JSON.
Includes --manifest flag for AI consumption contracts.
"""

import argparse
import json
import os
import sys
from typing import Any

import click
from pydantic import BaseModel, Field, validator

from shared.llm_provider import LLMMessage, get_provider


# ── Pydantic Models ───────────────────────────────────────────

class Answer(BaseModel):
    """A single answer choice."""
    text: str
    correct: bool
    explanation: str


class Question(BaseModel):
    """A multiple-choice question with 4 options."""
    question_text: str = Field(..., description="The question stem")
    options: list[Answer] = Field(
        ..., min_length=4, max_length=4, description="Exactly 4 answer options"
    )
    difficulty: str = Field(default="medium", description="Question difficulty")

    @validator("options")
    def exactly_one_correct(cls, v):
        if sum(1 for opt in v if opt.correct) != 1:
            raise ValueError("Exactly one option must be correct")
        return v


class QuizResponse(BaseModel):
    """Complete quiz response structure."""
    topic: str
    model: str
    question_count: int = Field(default=5, description="Number of questions")
    questions: list[Question] = Field(
        ..., min_length=1, description="List of generated questions"
    )
    generated_at: str = Field(default="")


class Manifest(BaseModel):
    """Machine-readable capabilities description (AI consumption contract)."""
    name: str = "quiz-generator"
    version: str = "1.0.0"
    description: str = "Generates multiple-choice questions on any topic"
    capabilities: list[str] = Field(default_factory=lambda: [
        "topic-quiz-generation",
        "multiple-choice-format",
        "difficulty-grading",
        "json-structured-output",
    ])
    input_schema: dict = Field(default_factory=lambda: {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Subject for quiz generation"},
            "count": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
        },
        "required": ["topic"],
    })
    output_schema: dict = Field(default_factory=lambda: {
        "type": "object",
        "properties": {
            "topic": {"type": "string"},
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question_text": {"type": "string"},
                        "options": {
                            "type": "array",
                            "items": {"type": "object"},
                        },
                    },
                },
            },
        },
    })
    endpoint: str = "/quiz/generate"
    auth: str = "api_key"


# ── Prompt Templates ──────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert educator and assessment designer.

Generate exactly {count} multiple-choice questions about the topic "{topic}".

For EACH question:
1. Create a clear question stem
2. Provide exactly 4 answer options (A, B, C, D)
3. Mark exactly ONE correct answer
4. Write a brief explanation for the correct answer

Rules:
- Questions should range from foundational to advanced
- Each question must have exactly one correct answer
- Explanations should be educational, not just "correct" or "incorrect"
- Avoid ambiguity in question wording
- Do not generate questions about yourself or your capabilities

Format your response as a JSON object matching this structure:
{
  "topic": "...",
  "questions": [
    {
      "question_text": "...",
      "options": [
        {"text": "...", "correct": true/false, "explanation": "..."},
        {"text": "...", "correct": false, "explanation": "..."},
        {"text": "...", "correct": false, "explanation": "..."},
        {"text": "...", "correct": false, "explanation": "..."},
      ],
      "difficulty": "easy|medium|hard"
    }
  ]
}
"""


# ── Core Functions ────────────────────────────────────────────

def generate_quiz(topic: str, count: int = 5) -> QuizResponse:
    """Generate a quiz using the LLM provider."""
    provider = get_provider()
    prompt = SYSTEM_PROMPT.format(topic=topic, count=count)

    messages = [
        LLMMessage(role="system", content="You are an expert educator."),
        LLMMessage(role="user", content=prompt),
    ]

    response = provider.complete(
        messages=messages,
        model="gpt-4o",
        temperature=0.7,
        max_tokens=4096,
    )

    # Parse JSON from response
    try:
        data = json.loads(response.content)
    except (json.JSONDecodeError, AttributeError) as e:
        click.echo(f"❌ Failed to parse LLM response: {e}", err=True)
        sys.exit(1)

    quiz = QuizResponse(
        topic=data["topic"],
        model="gpt-4o",
        questions=data["questions"],
    )
    return quiz


def generate_with_structured_output(topic: str, count: int = 5) -> QuizResponse:
    """Generate a quiz using structured output / JSON mode."""
    provider = get_provider()
    prompt = f"Generate {count} multiple-choice questions about '{topic}'. Return ONLY valid JSON."

    messages = [
        LLMMessage(role="user", content=prompt),
    ]

    response = provider.complete(
        messages=messages,
        model="gpt-4o",
        temperature=0.3,
        max_tokens=4096,
    )

    data = json.loads(response.content)
    return QuizResponse(topic=data["topic"], model="gpt-4o", questions=data["questions"])


# ── CLI ───────────────────────────────────────────────────────

@click.group()
def cli():
    """Quiz Generator — Module 1: LLM Fundamentals & Prompt Engineering"""
    pass


@cli.command("generate")
@click.argument("topic")
@click.option("--count", default=5, help="Number of questions to generate")
@click.option("--manifest", is_flag=True, help="Output AI consumption contract manifest")
@click.option("--json", "output_json", is_flag=True, help="Output raw JSON")
def generate(topic, count, manifest, output_json):
    """Generate multiple-choice questions on TOPIC."""
    if manifest:
        # AI consumption contract — machine-readable capabilities
        m = Manifest()
        click.echo(m.model_dump_json(indent=2))
        return

    quiz = generate_quiz(topic, count)

    if output_json:
        click.echo(quiz.model_dump_json(indent=2))
    else:
        # Pretty formatted output
        click.echo(f"\n📝 Quiz: {quiz.topic}\n")
        click.echo("=" * 60)
        for i, q in enumerate(quiz.questions, 1):
            click.echo(f"\nQ{i}. [{q.difficulty.upper()}] {q.question_text}")
            for j, opt in enumerate(q.options, 65):  # A, B, C, D
                marker = "✓" if opt.correct else " "
                click.echo(f"  {chr(j)}. {marker} {opt.text}")
            click.echo(f"     → Explanation: {q.options[0].explanation if q.options[0].correct else [o for o in q.options if o.correct][0].explanation}")
        click.echo("\n" + "=" * 60)


@cli.command("manifest")
def manifest_cmd():
    """Output AI consumption contract manifest."""
    m = Manifest()
    click.echo(m.model_dump_json(indent=2))


if __name__ == "__main__":
    cli()
