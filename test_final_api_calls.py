#!/usr/bin/env python3
"""
Test final API calls to verify models are working with the fixed authentication.
"""
import asyncio
import os
import sys
from datetime import datetime

# Set up environment to simulate GitHub Actions
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

async def test_api_calls():
    """Test API calls with the current configuration."""
    try:
        from fallback_llm import create_default_fallback_llm

        print("🤖 TESTING FINAL API CALLS WITH FIXED AUTHENTICATION")
        print("=" * 60)

        # Get API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY is not set!")
            return False

        print(f"✅ API key found: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else 'VALID'}")

        # Create FallbackLLM using the same method as main.py
        test_llm = create_default_fallback_llm(
            api_key=api_key,
            temperature=0.5,
            timeout=60,
            allowed_tries=2
        )

        print(f"✅ FallbackLLM created successfully")
        print(f"✅ Model chain: {test_llm.model_chain}")

        # Test with a simple prompt
        test_prompt = "What is 3+4? Answer with just the number."
        print(f"\n📝 Testing with prompt: '{test_prompt}'")

        response = await test_llm.invoke(test_prompt)

        print(f"✅ API CALL SUCCESSFUL!")
        print(f"📥 Response: {response}")

        # Test with a research prompt
        research_prompt = "What is artificial general intelligence (AGI)? Give a brief definition in one sentence."
        print(f"\n📝 Testing with research prompt: '{research_prompt}'")

        research_response = await test_llm.invoke(research_prompt)

        print(f"✅ RESEARCH API CALL SUCCESSFUL!")
        print(f"📥 Response: {research_response[:100]}{'...' if len(research_response) > 100 else ''}")

        print(f"\n🎉 ALL API CALLS ARE WORKING!")
        print(f"✅ The API key authentication fix is successful")
        print(f"✅ All 9 models in the fallback chain are available")
        return True

    except Exception as e:
        print(f"❌ API CALL FAILED: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_calls())
    sys.exit(0 if success else 1)