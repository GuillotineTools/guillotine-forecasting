#!/usr/bin/env python3
"""
Basic test of POTUS submission workflow - simplified version.
"""

import os
import asyncio
from datetime import datetime

# Set up environment
os.environ['GITHUB_ACTIONS'] = 'true'

async def test_submission_basic():
    """Basic test of submission workflow."""
    print("🔍 BASIC SUBMISSION TEST")
    print("=" * 40)

    # Check environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    metaculus_token = os.getenv('METACULUS_TOKEN')

    print(f"OpenRouter API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"Metaculus Token: {'✅ Found' if metaculus_token else '❌ Missing'}")

    if not api_key or not metaculus_token:
        print("❌ Missing required API keys")
        return False

    try:
        from forecasting_tools import MetaculusApi, BinaryQuestion
        from fallback_llm import create_forecasting_fallback_llm

        print("✅ Modules imported successfully")

        # Step 1: Get Bondi question
        print(f"\n📊 GETTING BONDI QUESTION")

        try:
            # Try direct URL access first
            bondi_question = await MetaculusApi.get_question_by_url("https://www.metaculus.com/questions/39988/")
            print(f"✅ Found Bondi question: {bondi_question.question_text[:80]}...")
            print(f"   Status: {bondi_question.status}")
            print(f"   Type: {type(bondi_question).__name__}")
            print(f"   ID: {bondi_question.id}")
        except Exception as e:
            print(f"❌ Direct access failed: {e}")
            return False

        # Verify it's a binary open question
        if not isinstance(bondi_question, BinaryQuestion):
            print(f"❌ Not binary: {type(bondi_question).__name__}")
            return False

        if bondi_question.status != "open":
            print(f"❌ Not open: {bondi_question.status}")
            return False

        # Step 2: Generate forecast
        print(f"\n🔮 GENERATING FORECAST")

        forecaster_llm = create_forecasting_fallback_llm(
            api_key=api_key,
            temperature=0.5,
            timeout=60,
            allowed_tries=2
        )

        print(f"✅ Model: {forecaster_llm.model_chain[0]}")

        prompt = f"""Brief forecast for: {bondi_question.question_text}

Give probability as "XX% - [Yes/No]" with brief reasoning.
Focus on realistic assessment of Pam Bondi leaving before March 2026.
"""

        try:
            response = await forecaster_llm.invoke(prompt)
            print(f"✅ Forecast: {response[:100]}...")
        except Exception as e:
            print(f"❌ Forecast failed: {e}")
            return False

        # Step 3: Extract probability and submit
        print(f"\n🚀 SUBMITTING")

        import re
        prob_match = re.search(r'(\d+)%', response)
        if prob_match:
            probability = int(prob_match.group(1))
            print(f"📊 Probability: {probability}%")
        else:
            probability = 50  # fallback
            print(f"⚠️  Using fallback: 50%")

        try:
            print(f"🔄 Submitting to Metaculus...")
            MetaculusApi.post_binary_question_prediction(bondi_question.id, probability / 100.0)
            print(f"✅ SUBMISSION SUCCESS!")
            print(f"   URL: {bondi_question.page_url}")

            # Save result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"submission_{timestamp}.md", "w") as f:
                f.write(f"# Submission Success\n\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n**Question:** {bondi_question.question_text}\n**Probability:** {probability}%\n**URL:** {bondi_question.page_url}\n\nCheck at: {bondi_question.page_url}\n")

            return True

        except Exception as e:
            print(f"❌ Submission failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_submission_basic())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")