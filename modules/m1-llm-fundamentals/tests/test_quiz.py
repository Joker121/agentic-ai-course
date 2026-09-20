"""Tests for Module 1: LLM Fundamentals & Prompt Engineering."""

import json
import pytest
from pydantic import ValidationError
from modules.m1_llm_fundamentals.main import (
    QuizResponse,
    Question,
    Answer,
    Manifest,
    generate_quiz,
)


class TestAnswer:
    def test_answer_creation(self):
        a = Answer(text="42", correct=True, explanation="It's the answer to everything")
        assert a.text == "42"
        assert a.correct is True

    def test_answer_cannot_have_multiple_correct(self):
        with pytest.raises(ValidationError):
            Question(
                question_text="What is 2+2?",
                options=[
                    Answer(text="3", correct=False, explanation="Wrong"),
                    Answer(text="4", correct=True, explanation="Correct"),
                    Answer(text="5", correct=True, explanation="Also correct"),  # Two correct!
                    Answer(text="6", correct=False, explanation="Wrong"),
                ],
            )


class TestQuestion:
    def test_question_creation(self):
        q = Question(
            question_text="What is the capital of France?",
            options=[
                Answer(text="Paris", correct=True, explanation="It is."),
                Answer(text="London", correct=False, explanation="No."),
                Answer(text="Berlin", correct=False, explanation="No."),
                Answer(text="Madrid", correct=False, explanation="No."),
            ],
        )
        assert q.question_text == "What is the capital of France?"

    def test_question_requires_four_options(self):
        with pytest.raises(ValidationError):
            Question(
                question_text="Test?",
                options=[
                    Answer(text="A", correct=True, explanation="Yes"),
                ],
            )


class TestManifest:
    def test_manifest_schema(self):
        m = Manifest()
        d = m.model_dump()
        assert d["name"] == "quiz-generator"
        assert len(d["capabilities"]) == 4
        assert "input_schema" in d
        assert "output_schema" in d

    def test_manifest_json_output(self):
        m = Manifest()
        json_str = m.model_dump_json()
        parsed = json.loads(json_str)
        assert parsed["version"] == "1.0.0"
        assert parsed["endpoint"] == "/quiz/generate"
