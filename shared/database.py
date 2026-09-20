"""Postgres connection pool with pgvector support."""

import os
from contextlib import asynccontextmanager
from typing import Optional
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_ai",
)

engine = create_async_engine(DATABASE_URL, echo=os.getenv("DEBUG") == "true", pool_size=10)
session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


@asynccontextmanager
async def get_connection():
    """Get a raw asyncpg connection for pgvector operations."""
    conn = await asyncpg.connect(os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/agentic_ai"))
    try:
        yield conn
    finally:
        await conn.close()


async def init_db():
    """Initialize the database and pgvector extension."""
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: None)  # Tables created via ORM
    # Enable pgvector extension
    async with get_connection() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")


async def get_session() -> AsyncSession:
    """Get an async session."""
    async with session_factory() as session:
        yield session
