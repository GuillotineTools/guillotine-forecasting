import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def test_slug_vs_id():
    print("Testing slug vs ID...")
    
    # Test with ID
    try:
        print("\n1. Using ID...")
        api_filter1 = ApiFilter(
            allowed_tournaments=[32813],  # ID
            allowed_statuses=["open"],
        )
        print(f"ApiFilter with ID: {api_filter1}")
        questions1 = await MetaculusApi.get_questions_matching_filter(api_filter1)
        print(f"Found {len(questions1)} questions with ID")
        for q in questions1[:3]:  # Just show first 3
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with ID: {e}")
        
    # Test with slug
    try:
        print("\n2. Using slug...")
        api_filter2 = ApiFilter(
            allowed_tournaments=["fall-aib-2025"],  # Slug
            allowed_statuses=["open"],
        )
        print(f"ApiFilter with slug: {api_filter2}")
        questions2 = await MetaculusApi.get_questions_matching_filter(api_filter2)
        print(f"Found {len(questions2)} questions with slug")
        for q in questions2[:3]:  # Just show first 3
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with slug: {e}")

if __name__ == "__main__":
    asyncio.run(test_slug_vs_id())