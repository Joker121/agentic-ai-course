"""Module 2: RAG Chatbot — RAG pipeline over documents with pgvector + Redis."""

import os
from typing import List, Optional

import fastapi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.database import Base, engine, init_db
from shared.redis_client import cache_message, get_cached_message

app = FastAPI(title="RAG Agent", version="0.1.0")


# ── Data Models ───────────────────────────────────────────────

class Query(BaseModel):
    question: str
    top_k: int = 3
    use_cache: bool = True


class Chunk(BaseModel):
    text: str
    source: str
    embedding: List[float]
    metadata: dict = {}


class RetrievalResult(BaseModel):
    chunks: List[Chunk]
    answer: str
    sources: List[str]


class DocumentUpload(BaseModel):
    text: str
    source: str
    chunk_size: int = 500
    overlap: int = 50


# ── RAG Pipeline ──────────────────────────────────────────────

class RAGPipeline:
    """Full RAG pipeline: chunking, embedding, retrieval, reranking."""

    def __init__(self):
        self.chunks: List[Chunk] = []
        self.provider = None

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        return chunks

    async def add_document(self, doc: DocumentUpload):
        """Add a document to the vector store."""
        from shared.llm_provider import get_provider
        self.provider = get_provider()

        chunks = self.chunk_text(doc.text, doc.chunk_size, doc.overlap)
        texts = chunks
        embeddings = await self.provider.embed(texts)

        for i, (text, emb) in enumerate(zip(texts, embeddings)):
            chunk = Chunk(
                text=text,
                source=doc.source,
                embedding=emb,
                metadata={"chunk_index": i, "total_chunks": len(chunks)},
            )
            self.chunks.append(chunk)

    async def retrieve(self, query: str, top_k: int = 3) -> List[Chunk]:
        """Retrieve relevant chunks using cosine similarity."""
        from shared.llm_provider import get_provider
        if not self.provider:
            self.provider = get_provider()

        query_embedding = await self.provider.embed([query])[0]

        # Cosine similarity
        results = []
        for chunk in self.chunks:
            similarity = self._cosine_similarity(query_embedding, chunk.embedding)
            results.append((similarity, chunk))

        results.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in results[:top_k]]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def answer(self, question: str, top_k: int = 3) -> str:
        """Generate an answer to a question using retrieved context."""
        from shared.llm_provider import LLMMessage, get_provider

        chunks = await self.retrieve(question, top_k)
        context = "\n\n".join(
            f"[Source: {c.source}] {c.text}" for c in chunks
        )

        prompt = f"""Use the following context to answer the question.
If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {question}

Answer:"""

        provider = get_provider()
        response = await provider.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            temperature=0.3,
            max_tokens=1024,
        )
        return response.content


# ── FastAPI Endpoints ─────────────────────────────────────────

rag_pipeline = RAGPipeline()


@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/upload")
async def upload_document(doc: DocumentUpload):
    """Upload a document to the RAG knowledge base."""
    await rag_pipeline.add_document(doc)
    return {
        "status": "uploaded",
        "chunks_created": len(rag_pipeline.chunks),
        "source": doc.source,
    }


@app.post("/query", response_model=RetrievalResult)
async def query(query: Query):
    """Query the knowledge base and get an answer."""
    # Check cache
    if query.use_cache:
        cached = await get_cached_message(f"rag:{query.question}")
        if cached:
            return RetrievalResult(**cached)

    # Retrieve chunks and generate answer
    chunks = await rag_pipeline.retrieve(query.question, query.top_k)
    answer = await rag_pipeline.answer(query.question, query.top_k)
    sources = list(set(c.source for c in chunks))

    results = RetrievalResult(
        chunks=chunks,
        answer=answer,
        sources=sources,
    )

    # Cache the result
    if query.use_cache:
        await cache_message(f"rag:{query.question}", results.model_dump(), ttl=1800)

    return results


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rag-agent", "chunks_loaded": len(rag_pipeline.chunks)}


@app.get("/chunks")
async def list_chunks():
    """List all chunks in the knowledge base."""
    return {
        "total_chunks": len(rag_pipeline.chunks),
        "chunks": [
            {"source": c.source, "chunk_index": c.metadata.get("chunk_index"), "text_preview": c.text[:100]}
            for c in rag_pipeline.chunks
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
