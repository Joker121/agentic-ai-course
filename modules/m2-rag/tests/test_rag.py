"""Tests for Module 2: RAG Chatbot."""

import pytest
from pydantic import ValidationError
from modules.m2_rag.main import (
    Chunk,
    Query,
    DocumentUpload,
    RetrievalResult,
    RAGPipeline,
)


class TestChunk:
    def test_chunk_creation(self):
        c = Chunk(
            text="Hello world",
            source="test.md",
            embedding=[0.1, 0.2, 0.3],
        )
        assert c.source == "test.md"

    def test_embedding_length(self):
        c = Chunk(
            text="Test",
            source="test.md",
            embedding=[0.0] * 1536,
        )
        assert len(c.embedding) == 1536


class TestQuery:
    def test_query_creation(self):
        q = Query(question="What is AI?", top_k=3)
        assert q.question == "What is AI?"
        assert q.top_k == 3

    def test_query_requires_question(self):
        with pytest.raises(ValidationError):
            Query(question="")


class TestDocumentUpload:
    def test_upload_creation(self):
        doc = DocumentUpload(text="Hello", source="doc.md")
        assert doc.chunk_size == 500

    def test_custom_chunk_size(self):
        doc = DocumentUpload(text="Hello", source="doc.md", chunk_size=1000)
        assert doc.chunk_size == 1000


class TestRAGPipeline:
    def test_chunking(self):
        pipeline = RAGPipeline()
        text = " " .join(["word"] * 20)
        chunks = pipeline.chunk_text(text, chunk_size=50, overlap=10)
        assert len(chunks) > 0
        assert all(len(c) > 0 for c in chunks)

    def test_cosine_similarity(self):
        pipeline = RAGPipeline()
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        assert pipeline._cosine_similarity(a, b) == 1.0

        c = [0.0, 1.0, 0.0]
        assert pipeline._cosine_similarity(a, c) == 0.0
