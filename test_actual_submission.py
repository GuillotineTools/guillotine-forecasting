#!/usr/bin/env python3
"""
Direct test of actual submission using the known working patterns.
"""

import os
import asyncio
import requests
from datetime import datetime

os.environ['GITHUB_ACTIONS'] = 'true'

async def test_actual_submission():
    print("🚀 DIRECT SUBMISSION TEST")
    print("=" * 40)

    # Check environment
    metaculus_token = os.getenv('METACULUS_TOKEN')
    api_key = os.getenv('OPENROUTER_API_KEY')

    print(f"Metaculus Token: {'✅' if metaculus_token else '❌'}")
    print(f"OpenRouter Key: {'✅' if api_key else '❌'}")

    if not metaculus_token:
        print("❌ No Metaculus token")
        return False

    # Use direct HTTP API for everything
    headers = {
        'Authorization': f'Token {metaculus_token}',
        'Content-Type': 'application/json'
    }

    try:
        # Step 1: Get Bondi question directly via API
        print("\n📊 STEP 1: GET BONDI QUESTION")
        response = requests.get('https://www.metaculus.com/api/posts/39988/', headers=headers)

        if response.status_code != 200:
            print(f"❌ Failed to get Bondi question: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        question_data = response.json()
        print(f"✅ Bondi question: {question_data.get('title', 'No title')[:60]}...")
        print(f"   Status: {question_data.get('status', 'Unknown')}")
        print(f"   Type: {question_data.get('type', 'Unknown')}")
        print(f"   ID: {question_data.get('id', 'No ID')}")

        # Step 2: Generate a simple forecast (no LLM needed for test)
        print("\n🔮 STEP 2: GENERATE TEST FORECAST")

        # Use a reasonable test probability for Pam Bondi leaving
        # This is just for testing the submission mechanism
        probability = 30  # 30% chance
        print(f"✅ Test forecast: {probability}% (Yes)")

        # Step 3: Submit the forecast using the correct API endpoint
        print("\n🚀 STEP 3: SUBMIT FORECAST")

        # Based on the main_with_no_framework.py pattern
        submission_url = 'https://www.metaculus.com/api/questions/forecast/'

        submission_data = [
            {
                "question": 39988,  # Use the numeric ID directly
                "prediction": probability / 100.0,  # Convert to decimal
            }
        ]

        print(f"🔄 Submitting to: {submission_url}")
        print(f"   Data: {submission_data}")

        response = requests.post(submission_url, headers=headers, json=submission_data)

        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✅ SUBMISSION SUCCESS!")

            # Step 4: Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"actual_submission_{timestamp}.md", "w") as f:
                f.write(f"""# Actual Submission Test Results

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** ✅ SUBMITTED SUCCESSFULLY

## Question
**ID:** 39988
**Title:** {question_data.get('title', 'No title')}
**URL:** https://www.metaculus.com/questions/39988/

## Forecast Submitted
**Probability:** {probability}%
**Prediction:** Yes
**Method:** Direct HTTP API (test)

## API Response
**Status Code:** {response.status_code}
**Response:** {response.text}

## Verification
Check the forecast at: [https://www.metaculus.com/questions/39988/](https://www.metaculus.com/questions/39988/)

The forecast should appear in the prediction history on the question page.
""")

            print(f"✅ Results saved: actual_submission_{timestamp}.md")
            return True

        else:
            print(f"❌ Submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_actual_submission())
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")