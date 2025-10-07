#!/usr/bin/env python3
"""
Simple test to check OpenRouter API key format and connectivity.
"""

import os
import requests
import json

def test_openrouter_simple():
    print("🔍 SIMPLE OPENROUTER TEST")
    print("=" * 40)

    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"API Key: {api_key}")
    print(f"Length: {len(api_key) if api_key else 0}")

    if not api_key:
        print("❌ No API key found")
        return False

    # Check if it looks like a real OpenRouter key
    if api_key == "test_key" or len(api_key) < 20:
        print("❌ API key appears to be a test/dummy key")
        return False

    # Test actual API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": "Say 'Hello OpenRouter'"}]
    }

    try:
        print("🔄 Testing OpenRouter API call...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            message = result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
            print(f"✅ OpenRouter API working!")
            print(f"Response: {message}")
            return True
        else:
            print(f"❌ OpenRouter API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ OpenRouter API error: {e}")
        return False

if __name__ == "__main__":
    success = test_openrouter_simple()
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")