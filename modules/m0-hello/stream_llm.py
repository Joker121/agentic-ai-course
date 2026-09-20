"""Module 0 Hands-On Task: LLM API streaming CLI tool."""

import asyncio
import os
import sys
from typing import AsyncIterator

import httpx


def print_progress(text: str) -> None:
    """Print text progressively to simulate streaming."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
    sys.stdout.write("\n")


async def stream_llm_response(
    prompt: str,
    api_key: str = None,
    model: str = "gpt-4o",
    base_url: str = "https://api.openai.com/v1",
) -> AsyncIterator[str]:
    """Stream LLM response token by token."""
    headers = {
        "Authorization": f"Bearer {api_key or os.getenv('LLM_API_KEY')}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": 512,
    }

    async with httpx.AsyncClient() as client:
        async with client.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    import json
                    chunk = json.loads(data)
                    content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        yield content


async def main():
    """Entry point for streaming LLM response."""
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Explain agentic AI in 3 sentences."

    print(f"\n🎯 Prompt: {prompt}\n")
    print("🤖 Streaming response:\n")

    async for token in stream_llm_response(prompt):
        sys.stdout.write(token)
        sys.stdout.flush()

    print("\n\n✅ Stream complete.")


if __name__ == "__main__":
    asyncio.run(main())
