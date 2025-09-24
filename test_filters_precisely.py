import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def test_filters_precisely():
    print("Testing filters precisely...")
    
    # Test 1: Using the exact same parameters as get_all_open_questions_from_tournament
    try:
        print("\n1. Using exact same parameters as get_all_open_questions_from_tournament...")
        tournament_id = MetaculusApi.CURRENT_AI_COMPETITION_ID
        print(f"Tournament ID: {tournament_id}")
        
        api_filter1 = ApiFilter(
            allowed_tournaments=[tournament_id],
            allowed_statuses=["open"],
            group_question_mode="unpack_subquestions",
        )
        print(f"ApiFilter: {api_filter1}")
        questions1 = await MetaculusApi.get_questions_matching_filter(api_filter1)
        print(f"Found {len(questions1)} questions using exact same parameters")
        for q in questions1[:3]:  # Just show first 3
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with exact same parameters: {e}")
        import traceback
        traceback.print_exc()
        
    # Test 2: Using parameters that worked in our previous test
    try:
        print("\n2. Using parameters that worked before...")
        api_filter2 = ApiFilter(
            statuses=["open"],  # This is not a valid ApiFilter parameter!
            tournaments=[MetaculusApi.CURRENT_AI_COMPETITION_ID],  # This is not a valid ApiFilter parameter!
        )
        print(f"ApiFilter: {api_filter2}")
        questions2 = await MetaculusApi.get_questions_matching_filter(api_filter2)
        print(f"Found {len(questions2)} questions using working parameters")
        for q in questions2[:3]:  # Just show first 3
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with working parameters (expected): {e}")
        
    # Test 3: Manual check of what get_all_open_questions_from_tournament does
    try:
        print("\n3. Manual check of what get_all_open_questions_from_tournament does...")
        tournament_id = MetaculusApi.CURRENT_AI_COMPETITION_ID
        api_filter3 = ApiFilter(
            allowed_tournaments=[tournament_id],
            allowed_statuses=["open"],
            group_question_mode="unpack_subquestions",
        )
        print(f"ApiFilter (manually created): {api_filter3}")
        
        # This is exactly what get_all_open_questions_from_tournament does
        questions3 = asyncio.run(MetaculusApi.get_questions_matching_filter(api_filter3))
        print(f"Found {len(questions3)} questions (manual check)")
        for q in questions3[:3]:  # Just show first 3
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with manual check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_filters_precisely())