#!/usr/bin/env python3
"""Test script for semantic search with Qdrant."""

import requests
import json

BASE_URL = "http://localhost:8100"

def test_search(query: str):
    """Test semantic search with a query."""
    print(f"\n{'='*80}")
    print(f"Testing query: '{query}'")
    print(f"{'='*80}")

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": query,
            "conversation_id": "test-123"
        },
        stream=True
    )

    print("\nResponse:")
    print("-" * 80)

    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = line_str[6:]
                if data != '[DONE]':
                    try:
                        chunk = json.loads(data)
                        if 'content' in chunk:
                            print(chunk['content'], end='', flush=True)
                    except json.JSONDecodeError:
                        pass

    print("\n" + "="*80)

def main():
    # Test health
    print("Checking backend health...")
    health = requests.get(f"{BASE_URL}/health").json()
    print(f"✓ Backend healthy")
    print(f"  Documents: {health['documents_loaded']}")
    print(f"  Chunks: {health['chunks_created']}")

    # Test search queries
    test_search("where is the meat department?")
    test_search("what electrical work is needed for the bakery?")
    test_search("tell me about the refrigeration system")

if __name__ == "__main__":
    main()
