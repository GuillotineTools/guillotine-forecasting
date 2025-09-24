import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi

async def check_tournament_methods():
    print("Checking tournament methods...")
    
    # Method 1: Using get_all_open_questions_from_tournament with ID
    try:
        print("\n1. Using get_all_open_questions_from_tournament with ID...")
        questions1 = MetaculusApi.get_all_open_questions_from_tournament(
            MetaculusApi.CURRENT_AI_COMPETITION_ID
        )
        print(f"Found {len(questions1)} questions using ID method")
        for q in questions1:
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with ID method: {e}")
        
    # Method 2: Using get_all_open_questions_from_tournament with slug
    try:
        print("\n2. Using get_all_open_questions_from_tournament with slug...")
        questions2 = MetaculusApi.get_all_open_questions_from_tournament(
            "fall-aib-2025"
        )
        print(f"Found {len(questions2)} questions using slug method")
        for q in questions2:
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with slug method: {e}")
        
    # Method 3: Using get_questions_matching_filter with ID
    try:
        print("\n3. Using get_questions_matching_filter with ID...")
        from forecasting_tools.helpers.metaculus_api import ApiFilter
        api_filter3 = ApiFilter(
            statuses=["open"],
            tournaments=[MetaculusApi.CURRENT_AI_COMPETITION_ID]
        )
        questions3 = await MetaculusApi.get_questions_matching_filter(api_filter3)
        print(f"Found {len(questions3)} questions using filter with ID")
        for q in questions3:
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with filter ID method: {e}")
        
    # Method 4: Using get_questions_matching_filter with slug
    try:
        print("\n4. Using get_questions_matching_filter with slug...")
        from forecasting_tools.helpers.metaculus_api import ApiFilter
        api_filter4 = ApiFilter(
            statuses=["open"],
            tournaments=["fall-aib-2025"]
        )
        questions4 = await MetaculusApi.get_questions_matching_filter(api_filter4)
        print(f"Found {len(questions4)} questions using filter with slug")
        for q in questions4:
            print(f"  - {q.page_url}: {q.question_text}")
    except Exception as e:
        print(f"Error with filter slug method: {e}")

if __name__ == "__main__":
    asyncio.run(check_tournament_methods())