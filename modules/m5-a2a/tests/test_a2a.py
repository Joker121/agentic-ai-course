"""Tests for Module 5: A2A Multi-Agent System."""

import pytest
from pydantic import ValidationError


class TestA2AMessage:
    def test_message_structure(self):
        from modules.m5_a2a.main import A2AMessage, A2AResponse, AgentCard

        msg = A2AMessage(
            message_id="test-123",
            sender="orchestrator",
            recipient="researcher-a2a",
            type="research_request",
            payload={"question": "What is AI?"},
        )
        assert msg.message_id == "test-123"
        assert msg.type == "research_request"

    def test_response_structure(self):
        from modules.m5_a2a.main import A2AResponse

        resp = A2AResponse(
            message_id="test-123",
            status="queued",
            data={"task_type": "research"},
        )
        assert resp.status == "queued"


class TestAgentCard:
    def test_orchestrator_card(self):
        from modules.m5_a2a.main import ORCHESTRATOR_CARD
        card = ORCHESTRATOR_CARD.model_dump()
        assert card["name"] == "orchestrator"
        assert "task-routing" in card["capabilities"]
        assert "endpoint" in card

    def test_researcher_card(self):
        from modules.m5_a2a.main import RESEARCHER_CARD
        card = RESEARCHER_CARD.model_dump()
        assert card["name"] == "researcher-a2a"
        assert "web-search" in card["capabilities"]

    def test_writer_card(self):
        from modules.m5_a2a.main import WRITER_CARD
        card = WRITER_CARD.model_dump()
        assert card["name"] == "writer-a2a"
        assert "content-generation" in card["capabilities"]


class TestAgentCardFiles:
    def test_orchestrator_json(self):
        import json
        from pathlib import Path

        card_path = Path(__file__).parent.parent / "agent-cards" / "orchestrator.json"
        with open(card_path) as f:
            card = json.load(f)
        assert card["name"] == "orchestrator"
        assert len(card["capabilities"]) >= 2

    def test_researcher_json(self):
        import json
        from pathlib import Path

        card_path = Path(__file__).parent.parent / "agent-cards" / "researcher-a2a.json"
        with open(card_path) as f:
            card = json.load(f)
        assert card["name"] == "researcher-a2a"

    def test_writer_json(self):
        import json
        from pathlib import Path

        card_path = Path(__file__).parent.parent / "agent-cards" / "writer-a2a.json"
        with open(card_path) as f:
            card = json.load(f)
        assert card["name"] == "writer-a2a"

    def test_all_cards_have_required_fields(self):
        import json
        from pathlib import Path

        card_dir = Path(__file__).parent.parent / "agent-cards"
        for card_file in card_dir.glob("*.json"):
            with open(card_file) as f:
                card = json.load(f)
            for field in ["name", "version", "description", "endpoint", "capabilities"]:
                assert field in card, f"{card_file.name} missing {field}"
