#!/usr/bin/env python3
"""
Debug script to test POTUS forecast submission directly.
Tests the actual submission process without full workflow overhead.
"""

import os
import asyncio
import re
from datetime import datetime

# Set GitHub Actions environment
os.environ['GITHUB_ACTIONS'] = 'true'

async def test_submission():
    """Test the actual forecast submission process."""
    print("🔍 DEBUG: POTUS FORECAST SUBMISSION TEST")
    print("=" * 60)

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

        # Step 1: Get the Bondi question
        print("\n📊 STEP 1: GETTING BONDI QUESTION")

        try:
            print("🔍 Accessing POTUS-predictions tournament...")
            questions = MetaculusApi.get_all_open_questions_from_tournament("POTUS-predictions")
            print(f"✅ Found {len(questions)} questions in POTUS tournament")

            bondi_question = None
            for q in questions:
                q_text = getattr(q, 'question_text', '').lower()
                if 'bondi' in q_text or 'attorney general' in q_text:
                    bondi_question = q
                    print(f"✅ FOUND BONDI: {q.question_text[:80]}...")
                    print(f"   URL: {getattr(q, 'page_url', 'No URL')}")
                    print(f"   ID: {getattr(q, 'id', 'No ID')}")
                    print(f"   Status: {getattr(q, 'status', 'Unknown')}")
                    print(f"   Type: {type(q).__name__}")
                    break

            if not bondi_question:
                print("❌ Bondi question not found in tournament")
                # Try direct URL access as fallback
                try:
                    print("🔄 Trying direct URL access...")
                    bondi_question = await MetaculusApi.get_question_by_url("https://www.metaculus.com/questions/39988/")
                    print(f"✅ Found via direct URL: {bondi_question.question_text[:80]}...")
                except Exception as e:
                    print(f"❌ Direct URL access failed: {e}")
                    return False

        except Exception as e:
            print(f"❌ Tournament access failed: {e}")
            return False

        # Verify question
        if not isinstance(bondi_question, BinaryQuestion):
            print(f"❌ Question is not binary: {type(bondi_question).__name__}")
            return False

        if bondi_question.status != "open":
            print(f"❌ Question is not open: {bondi_question.status}")
            return False

        print(f"✅ CONFIRMED: Binary open question ready")

        # Step 2: Generate a simple forecast
        print(f"\n🔮 STEP 2: GENERATING FORECAST")

        forecaster_llm = create_forecasting_fallback_llm(
            api_key=api_key,
            temperature=0.5,
            timeout=60,
            allowed_tries=2
        )

        print(f"✅ Using model: {forecaster_llm.model_chain[0]}")

        forecast_prompt = f"""Analyze this question and provide a probability forecast:

Question: {bondi_question.question_text}

Task:
1. Consider the current political situation
2. Assess realistic probability (0-100%)
3. Format: "Probability: XX% - [Yes/No]"
4. Keep reasoning brief but evidence-based

Focus on the likelihood of Pam Bondi departing as Attorney General before March 2026.
"""

        try:
            print("🔄 Generating forecast...")
            forecast_response = await forecaster_llm.invoke(forecast_prompt)
            print(f"✅ Forecast generated: {forecast_response[:150]}...")
        except Exception as e:
            print(f"❌ Forecast generation failed: {e}")
            return False

        # Step 3: Extract probability
        print(f"\n📊 STEP 3: EXTRACTING PROBABILITY")

        probability_match = re.search(r'Probability:\s*(\d+)%', forecast_response)
        if probability_match:
            final_probability = int(probability_match.group(1))
            final_prediction = final_probability >= 50
            print(f"✅ Extracted: {final_probability}% ({'Yes' if final_prediction else 'No'})")
        else:
            print("❌ Could not extract probability")
            return False

        # Step 4: SUBMIT TO METACULUS
        print(f"\n🚀 STEP 4: SUBMITTING TO METACULUS")

        try:
            print(f"🔄 Submitting forecast...")
            print(f"   Question ID: {bondi_question.id}")
            print(f"   Probability: {final_probability}%")
            print(f"   Prediction: {'Yes' if final_prediction else 'No'}")

            # Submit the forecast
            MetaculusApi.post_binary_question_prediction(
                bondi_question.id,
                final_probability / 100.0
            )

            print(f"✅ FORECAST SUBMITTED SUCCESSFULLY!")
            print(f"   Check at: {bondi_question.page_url}")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"debug_submission_{timestamp}.md"

            content = f"""# POTUS Forecast Submission Debug Results

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** ✅ SUBMITTED TO METACULUS

## Question
**Text:** {bondi_question.question_text}
**URL:** {bondi_question.page_url}
**ID:** {bondi_question.id}

## Forecast Submitted
**Probability:** {final_probability}%
**Prediction:** {'Yes' if final_prediction else 'No'}
**Model:** {forecaster_llm.model_chain[0]}

## Forecast Output
{forecast_response}

## Verification
Check the forecast at: [{bondi_question.page_url}]({bondi_question.page_url})

The forecast should appear in the prediction history.
"""

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Debug results saved: {output_file}")
            return True

        except Exception as e:
            print(f"❌ SUBMISSION FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"❌ DEBUG SCRIPT FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_submission())
    if success:
        print(f"\n🎉 SUBMISSION TEST SUCCESSFUL!")
        print("✅ Forecast should be visible on Metaculus")
    else:
        print(f"\n❌ SUBMISSION TEST FAILED!")