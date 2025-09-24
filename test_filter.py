import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def test_filter_directly():
    print("Testing API filter directly...")
    
    # Test filter with ID
    try:
        print("\n1. Using ApiFilter with ID...")
        api_filter1 = ApiFilter(
            statuses=["open"],
            tournaments=[MetaculusApi.CURRENT_AI_COMPETITION_ID]
        )
        print(f"Filter: {api_filter1}")
        questions1 = await MetaculusApi.get_questions_matching_filter(api_filter1)
        print(f"Found {len(questions1)} questions using filter with ID")
        for q in questions1[:5]:  # Just show first 5
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with filter ID method: {e}")
        import traceback
        traceback.print_exc()
        
    # Test filter with slug
    try:
        print("\n2. Using ApiFilter with slug...")
        api_filter2 = ApiFilter(
            statuses=["open"],
            tournaments=["fall-aib-2025"]
        )
        print(f"Filter: {api_filter2}")
        questions2 = await MetaculusApi.get_questions_matching_filter(api_filter2)
        print(f"Found {len(questions2)} questions using filter with slug")
        for q in questions2[:5]:  # Just show first 5
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with filter slug method: {e}")
        import traceback
        traceback.print_exc()

def test_filter_sync():
    print("Testing API filter synchronously...")
    
    # Test the get_all_open_questions_from_tournament method step by step
    try:
        print("\n3. Testing get_all_open_questions_from_tournament step by step...")
        tournament_id = MetaculusApi.CURRENT_AI_COMPETITION_ID
        print(f"Tournament ID: {tournament_id}")
        
        api_filter = ApiFilter(
            allowed_tournaments=[tournament_id],
            allowed_statuses=["open"],
            group_question_mode="unpack_subquestions",
        )
        print(f"ApiFilter: {api_filter}")
        
        # This is what get_all_open_questions_from_tournament does
        questions = asyncio.run(MetaculusApi.get_questions_matching_filter(api_filter))
        print(f"Found {len(questions)} questions")
        for q in questions[:5]:  # Just show first 5
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with step by step method: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_filter_directly())
    test_filter_sync()