#!/usr/bin/env python3
"""
Minimal test to isolate API issues.
"""

import os
import asyncio

os.environ['GITHUB_ACTIONS'] = 'true'

async def test_minimal():
    print("🔍 MINIMAL API TEST")
    print("=" * 30)

    # Check environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    metaculus_token = os.getenv('METACULUS_TOKEN')

    print(f"OpenRouter Key: {'✅' if api_key else '❌'}")
    print(f"Metaculus Token: {'✅' if metaculus_token else '❌'}")

    if not metaculus_token:
        print("❌ No Metaculus token - can't test")
        return False

    try:
        # Test basic import
        print("Importing forecasting_tools...")
        from forecasting_tools import MetaculusApi
        print("✅ Import successful")

        # Test API connection
        print("Testing API connection...")

        # Method 1: Try direct question access
        try:
            print("🔍 Direct question access...")
            q = await MetaculusApi.get_question_by_url("https://www.metaculus.com/questions/39988/")
            print(f"✅ Direct access: {q.question_text[:60]}...")
            print(f"   Status: {q.status}")
            print(f"   Type: {type(q).__name__}")
            print(f"   ID: {q.id}")
            return True
        except Exception as e:
            print(f"❌ Direct access failed: {e}")

        # Method 2: Try tournament access
        try:
            print("🔍 Tournament access...")
            questions = MetaculusApi.get_all_open_questions_from_tournament("POTUS-predictions")
            print(f"✅ Tournament: {len(questions)} questions")
            return True
        except Exception as e:
            print(f"❌ Tournament access failed: {e}")

        # Method 3: Try filter access
        try:
            print("🔍 Filter access...")
            from forecasting_tools import ApiFilter
            f = ApiFilter(statuses=["open"], number_of_questions=5)
            questions = await MetaculusApi.get_questions_matching_filter(f)
            print(f"✅ Filter: {len(questions)} questions")
            return True
        except Exception as e:
            print(f"❌ Filter access failed: {e}")

        return False

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_minimal())
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")