#!/usr/bin/env python3
"""
Direct test of OpenRouter API to debug authentication issues.
"""

import os
import asyncio

os.environ['GITHUB_ACTIONS'] = 'true'

async def test_openrouter():
    print("🔍 DIRECT OPENROUTER API TEST")
    print("=" * 40)

    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"API Key: {'✅ Found' if api_key else '❌ Missing'}")
    if api_key:
        print(f"API Key length: {len(api_key)}")
        print(f"API Key format: {api_key[:10]}...{api_key[-10:]}")

    try:
        # Test litellm directly
        from litellm import acompletion

        print("Testing OpenRouter API with litellm...")

        # Simple test call
        response = await acompletion(
            model="openrouter/deepseek/deepseek-chat",
            messages=[{"role": "user", "content": "Say 'Hello world'"}],
            api_key=api_key
        )

        print(f"✅ OpenRouter API SUCCESS!")
        print(f"Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ OpenRouter API FAILED: {e}")
        print(f"Error type: {type(e).__name__}")

        # Try alternative model names
        print("\n🔄 Trying alternative model name...")
        try:
            response = await acompletion(
                model="deepseek/deepseek-chat",
                messages=[{"role": "user", "content": "Say 'Hello world'"}],
                api_key=api_key
            )
            print(f"✅ Alternative model SUCCESS!")
            print(f"Response: {response.choices[0].message.content}")
            return True
        except Exception as e2:
            print(f"❌ Alternative model also failed: {e2}")

        return False

if __name__ == "__main__":
    success = asyncio.run(test_openrouter())
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")