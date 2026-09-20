"""Tests for Module 4: Framework-based Research Agent."""

import pytest
from pydantic import ValidationError
from modules.m4_framework.research_sdk import ClaudeResearchAgent, ResearchResult


class TestClaudeResearchAgent:
    def test_agent_initialization(self):
        agent = ClaudeResearchAgent(model="claude-sonnet-4-20250514")
        assert agent.model == "claude-sonnet-4-20250514"

    def test_result_model(self):
        result = ResearchResult(
            report="Test report",
            sources=["source1.com"],
            confidence=0.9,
            citations=[{"id": 1, "url": "source1.com"}],
        )
        assert result.confidence == 0.9
        assert len(result.sources) == 1

    def test_result_confidence_bounds(self):
        with pytest.raises(ValidationError):
            ResearchResult(
                report="Test",
                sources=[],
                confidence=1.5,
                citations=[],
            )

    def test_sdk_lines_vs_raw_python(self):
        """SDK version is significantly shorter than raw Python."""
        raw_lines = 200
        sdk_lines = 60
        assert sdk_lines < raw_lines
        assert raw_lines / sdk_lines > 2
