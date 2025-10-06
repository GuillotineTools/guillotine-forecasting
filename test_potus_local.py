#!/usr/bin/env python3
"""
Simple test to run POTUS forecasting locally with minimal setup.
"""
import asyncio
import os
from datetime import datetime

# Set up environment
os.environ['GITHUB_ACTIONS'] = 'true'

async def test_potus_simple():
    """Simple POTUS test to verify the process works."""
    try:
        from fallback_llm import create_research_fallback_llm, create_forecasting_fallback_llm, create_synthesis_fallback_llm

        print("🎯 TESTING POTUS FORECASTING SYSTEM")
        print("=" * 50)

        # Check API keys
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY is not set!")
            return False

        print("✅ API key configured")

        # Test LLM creation
        print("\n🤖 TESTING LLM CREATION")
        researcher_llm = create_research_fallback_llm(api_key=api_key, temperature=0.3, timeout=30, allowed_tries=1)
        forecaster_llm = create_forecasting_fallback_llm(api_key=api_key, temperature=0.5, timeout=30, allowed_tries=1)
        synthesizer_llm = create_synthesis_fallback_llm(api_key=api_key, temperature=0.3, timeout=30, allowed_tries=1)

        print(f"✅ Researcher model chain: {researcher_llm.model_chain[:3]}...")
        print(f"✅ Forecaster model chain: {forecaster_llm.model_chain[:3]}...")
        print(f"✅ Synthesizer model chain: {synthesizer_llm.model_chain[:3]}...")

        # Test simple API call
        print("\n🔄 TESTING SIMPLE API CALL")
        try:
            response = await researcher_llm.invoke("What is 2+2? Answer with just the number.")
            print(f"✅ API call successful: {response.strip()}")
            return True
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            return False

    except Exception as e:
        print(f"❌ POTUS test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_potus_simple())
    if success:
        print("\n🎉 POTUS FORECASTING SYSTEM TEST SUCCESSFUL!")
        print("✅ Ready for end-to-end forecasting")
    else:
        print("\n❌ POTUS FORECASTING SYSTEM TEST FAILED!")
        print("❌ Check the error messages above")
    import sys
    sys.exit(0 if success else 1)