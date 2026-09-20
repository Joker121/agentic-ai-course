"""Redis client for conversation cache and inter-agent message queues."""

import os
import redis.asyncio as aioredis
from typing import Optional
import json

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or initialize the Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def cache_message(
    key: str,
    value: dict,
    ttl: int = 3600,
) -> None:
    """Cache a message with TTL."""
    r = await get_redis()
    await r.setex(key, ttl, json.dumps(value))


async def get_cached_message(key: str) -> Optional[dict]:
    """Retrieve a cached message."""
    r = await get_redis()
    value = await r.get(key)
    if value:
        return json.loads(value)
    return None


async def enqueue_task(queue_name: str, task: dict) -> None:
    """Enqueue a task to a Redis queue."""
    r = await get_redis()
    await r.rpush(queue_name, json.dumps(task))


async def dequeue_task(queue_name: str) -> Optional[dict]:
    """Dequeue a task from a Redis queue."""
    r = await get_redis()
    value = await r.lpop(queue_name)
    if value:
        return json.loads(value)
    return None


async def publish_message(channel: str, message: dict) -> None:
    """Publish a message to a Redis channel."""
    r = await get_redis()
    await r.publish(channel, json.dumps(message))


async def subscribe_to_channel(channel: str) -> aioredis.Channel:
    """Subscribe to a Redis pub/sub channel."""
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    return pubsub


async def close_redis() -> None:
    """Close the Redis client."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
