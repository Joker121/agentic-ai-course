"""Tests for Module 3: Research Agent."""

import pytest
from modules.m3_research.main import (
    ReActAgent,
    ResearchReport,
    AgentState,
    ToolCall,
)


class TestReActAgent:
    def test_agent_initialization(self):
        agent = ReActAgent(max_steps=5)
        assert agent.max_steps == 5
        assert len(agent.steps) == 0

    def test_thinking(self):
        agent = ReActAgent(max_steps=3)
        thought = agent.think("What is AI?", "")
        assert isinstance(thought, str)
        assert len(thought) > 0

    def test_action_parsing(self):
        agent = ReActAgent(max_steps=3)
        thought = "I need to search the web for more information."
        action = agent._parse_action(thought, "What is AI?")
        if action:
            assert action.name in ["web_search", "fetch_url"]

    def test_report_structure(self):
        report = ResearchReport(
            question="Test question",
            content="Test content",
            sources=["source1"],
            citations=[{"id": 1, "url": "source1"}],
        )
        assert report.question == "Test question"
        assert len(report.sources) == 1


class TestAgentState:
    def test_all_states(self):
        states = [e.value for e in AgentState]
        assert "thinking" in states
        assert "acting" in states
        assert "observing" in states
        assert "finished" in states


class TestToolCall:
    def test_tool_call_creation(self):
        tc = ToolCall(name="web_search", args={"query": "test"}, success=True)
        assert tc.name == "web_search"
        assert tc.args == {"query": "test"}
