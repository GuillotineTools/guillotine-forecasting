import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi

def test_direct_method():
    print("Testing get_all_open_questions_from_tournament directly...")
    
    # Test with ID
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
        import traceback
        traceback.print_exc()
        
    # Test with slug
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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_method()