import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi

async def check_tournaments():
    print("Checking available tournaments...")
    
    # Check current tournament IDs
    print(f"CURRENT_AI_COMPETITION_ID: {MetaculusApi.CURRENT_AI_COMPETITION_ID}")
    print(f"CURRENT_MINIBENCH_ID: {MetaculusApi.CURRENT_MINIBENCH_ID}")
    print(f"AIB_FALL_2025_ID: {MetaculusApi.AIB_FALL_2025_ID}")
    
    # Try to get questions from the Fall AIB 2025 tournament
    try:
        print("\nTrying to fetch questions from Fall AIB 2025 tournament...")
        questions = MetaculusApi.get_all_open_questions_from_tournament(
            MetaculusApi.AIB_FALL_2025_ID
        )
        print(f"Found {len(questions)} questions in Fall AIB 2025")
        for q in questions:
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error fetching questions from Fall AIB 2025: {e}")
        
    # Try to get questions using the slug method
    try:
        print("\nTrying to fetch questions using slug 'fall-aib-2025'...")
        from forecasting_tools.helpers.metaculus_api import ApiFilter
        api_filter = ApiFilter(
            statuses=["open"],
            tournaments=["fall-aib-2025"]
        )
        questions = await MetaculusApi.get_questions_matching_filter(api_filter)
        print(f"Found {len(questions)} questions using slug method")
        for q in questions:
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error fetching questions using slug method: {e}")

if __name__ == "__main__":
    asyncio.run(check_tournaments())