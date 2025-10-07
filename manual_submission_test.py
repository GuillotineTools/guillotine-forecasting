#!/usr/bin/env python3
"""
MANUAL SUBMISSION TEST - Bypass GitHub Actions Issues

This script can be run manually with real API keys to test submission.
Instructions:
1. Set your real API keys as environment variables:
   export METACULUS_TOKEN="your_real_metaculus_token"
   export OPENROUTER_API_KEY="your_real_openrouter_key"
2. Run: python3 manual_submission_test.py
3. Check https://www.metaculus.com/questions/39988/ for the forecast
"""

import os
import asyncio
import requests
import re
from datetime import datetime

async def manual_submission_test():
    print("🚀 MANUAL SUBMISSION TEST - BYPASS GITHUB ACTIONS")
    print("=" * 70)
    print(f"Running at: {datetime.now()}")
    print()

    # Check API keys
    metaculus_token = os.getenv('METACULUS_TOKEN')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')

    print(f"🔑 METACULUS_TOKEN: {'✅ SET' if metaculus_token and len(metaculus_token) > 20 else '❌ MISSING/INVALID'}")
    print(f"🔑 OPENROUTER_API_KEY: {'✅ SET' if openrouter_key and len(openrouter_key) > 20 else '❌ MISSING/INVALID'}")

    if not metaculus_token or len(metaculus_token) <= 20:
        print("❌ Set real METACULUS_TOKEN environment variable")
        return False

    try:
        # Step 1: Get Bondi question from Metaculus
        print(f"\n📊 STEP 1: GETTING BONDI QUESTION")
        headers = {
            'Authorization': f'Token {metaculus_token}',
            'Content-Type': 'application/json'
        }

        response = requests.get('https://www.metaculus.com/api/posts/39988/', headers=headers)

        if response.status_code != 200:
            print(f"❌ Failed to get Bondi question: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        question_data = response.json()
        print(f"✅ Question: {question_data.get('title', 'No title')}")
        print(f"   Status: {question_data.get('status', 'Unknown')}")
        print(f"   URL: https://www.metaculus.com/questions/39988/")

        # Step 2: Generate forecast (with or without LLM)
        print(f"\n🔮 STEP 2: GENERATING FORECAST")

        forecast_method = "algorithmic"
        probability = 25  # 25% chance Bondi leaves before March 2026

        # Try to use LLM if OpenRouter key is available
        if openrouter_key and len(openrouter_key) > 20:
            print("🤖 Attempting LLM forecast generation...")
            try:
                llm_headers = {
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json"
                }

                llm_data = {
                    "model": "deepseek/deepseek-chat",
                    "messages": [{
                        "role": "user",
                        "content": f"""Analyze this question and give a probability forecast:

Question: {question_data.get('title', '')}

Consider the current political situation and provide a realistic probability (0-100%) that Pam Bondi will be out as US Attorney General before March 2026.

Respond with only: "XX%" where XX is your probability assessment."""
                    }]
                }

                llm_response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=llm_headers,
                    json=llm_data,
                    timeout=30
                )

                if llm_response.status_code == 200:
                    result = llm_response.json()
                    llm_output = result.get('choices', [{}])[0].get('message', {}).get('content', '')

                    # Extract probability from LLM response
                    prob_match = re.search(r'(\d+)%', llm_output)
                    if prob_match:
                        probability = int(prob_match.group(1))
                        forecast_method = "LLM-generated"
                        print(f"✅ LLM forecast: {probability}%")
                    else:
                        print(f"⚠️ LLM response unclear, using algorithmic: {llm_output}")
                else:
                    print(f"⚠️ LLM failed ({llm_response.status_code}), using algorithmic forecast")

            except Exception as e:
                print(f"⚠️ LLM error: {e}, using algorithmic forecast")
        else:
            print("⚠️ No valid OpenRouter key, using algorithmic forecast")

        print(f"📊 Final forecast: {probability}% ({'Yes' if probability >= 50 else 'No'})")
        print(f"📋 Method: {forecast_method}")

        # Step 3: Submit to Metaculus
        print(f"\n🚀 STEP 3: SUBMITTING TO METACULUS")

        submission_data = [{
            "question": 39988,
            "prediction": probability / 100.0  # Convert to decimal
        }]

        print(f"🔄 Submitting forecast...")
        print(f"   Question ID: 39988")
        print(f"   Prediction: {probability}% ({probability / 100.0})")

        submission_response = requests.post(
            'https://www.metaculus.com/api/questions/forecast/',
            headers=headers,
            json=submission_data
        )

        print(f"📊 Submission status: {submission_response.status_code}")

        if submission_response.status_code == 200:
            print(f"✅ SUBMISSION SUCCESSFUL!")
            print(f"🎯 FORECAST SUBMITTED TO METACULUS")

            # Step 4: Save detailed results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = f"manual_submission_success_{timestamp}.txt"

            with open(result_file, "w") as f:
                f.write(f"""MANUAL SUBMISSION SUCCESS!

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: ✅ SUBMITTED SUCCESSFULLY

Question:
- ID: 39988
- Title: {question_data.get('title', 'No title')}
- URL: https://www.metaculus.com/questions/39988/

Forecast Submitted:
- Probability: {probability}%
- Prediction: {'Yes' if probability >= 50 else 'No'}
- Method: {forecast_method}

API Response:
- Status Code: {submission_response.status_code}
- Response: {submission_response.text}

Verification:
Check the forecast at: https://www.metaculus.com/questions/39988/

The forecast should appear in the prediction history on the question page.
""")

            print(f"📄 Results saved: {result_file}")
            print(f"\n🎉 SUCCESS! Check https://www.metaculus.com/questions/39988/ for your forecast!")
            return True

        else:
            print(f"❌ Submission failed: {submission_response.status_code}")
            print(f"Response: {submission_response.text}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("""
🚀 MANUAL SUBMISSION TEST INSTRUCTIONS
======================================

This script bypasses GitHub Actions and tests API submission directly.

STEP 1: Set your real API keys:
   export METACULUS_TOKEN="your_real_metaculus_token"
   export OPENROUTER_API_KEY="your_real_openrouter_key"

STEP 2: Run the test:
   python3 manual_submission_test.py

STEP 3: Check the result at:
   https://www.metaculus.com/questions/39988/

""")

    success = asyncio.run(manual_submission_test())

    if success:
        print(f"\n🎉 MANUAL TEST COMPLETED SUCCESSFULLY!")
        print(f"✅ Your forecast has been submitted to Metaculus")
    else:
        print(f"\n❌ MANUAL TEST FAILED!")
        print(f"Check API keys and try again")