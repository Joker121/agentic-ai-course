"""Smoke test script for deployment validation."""

import sys
import time
import httpx
import argparse


def smoke_test(env: str = "staging", base_url: str = None):
    """Run smoke tests against the deployed service."""
    if not base_url:
        base_url = {
            "staging": "https://staging.agentic-ai-course.dev",
            "production": "https://agentic-ai-course.dev",
        }.get(env, f"http://localhost:8000")

    print(f"🔥 Running smoke tests against {base_url} ({env})")
    print("=" * 60)

    all_passed = True

    # Test 1: Health check
    print("\n[1/4] Testing /health endpoint...")
    try:
        response = httpx.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("  ✅ Health check passed")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        all_passed = False

    # Test 2: Ready endpoint
    print("\n[2/4] Testing /ready endpoint...")
    try:
        response = httpx.get(f"{base_url}/ready", timeout=10)
        if response.status_code == 200:
            print("  ✅ Ready check passed")
        else:
            print(f"  ❌ Ready check failed: {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"  ❌ Ready check error: {e}")
        all_passed = False

    # Test 3: Agent cards endpoint
    print("\n[3/4] Testing /a2a/card endpoint...")
    try:
        response = httpx.get(f"{base_url}/a2a/card", timeout=10)
        if response.status_code == 200:
            card = response.json()
            print(f"  ✅ Agent card retrieved: {card.get('name', 'unknown')}")
        else:
            print(f"  ❌ Agent card fetch failed: {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"  ❌ Agent card error: {e}")
        all_passed = False

    # Test 4: LLM connectivity (if API key available)
    print("\n[4/4] Testing LLM connectivity...")
    try:
        api_key = __import__("os").environ.get("LLM_API_KEY")
        if api_key:
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                json={"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 5},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            if response.status_code == 200:
                print("  ✅ LLM API connectivity confirmed")
            else:
                print(f"  ⚠️  LLM API returned {response.status_code}")
        else:
            print("  ⚠️  LLM_API_KEY not set, skipping LLM test")
    except Exception as e:
        print(f"  ❌ LLM test error: {e}")
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All smoke tests passed!")
        return 0
    else:
        print("❌ Some smoke tests failed. Check logs.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test deployment")
    parser.add_argument("--env", choices=["staging", "production"], default="staging")
    parser.add_argument("--base-url", type=str, default=None)
    args = parser.parse_args()

    sys.exit(smoke_test(env=args.env, base_url=args.base_url))
