import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def test_fixed_implementation():
    print("Testing fixed implementation with a tournament that has open questions...")
    
    # Test with tournament ID 32828 which has open questions
    try:
        print("\nTesting with tournament ID 32828 (Metaculus Cup Fall 2025)...")
        fall_cup_filter = ApiFilter(
            allowed_statuses=["open"],
            allowed_tournaments=[32828]
        )
        fall_cup_questions = await MetaculusApi.get_questions_matching_filter(fall_cup_filter)
        print(f"Found {len(fall_cup_questions)} open questions in Metaculus Cup Fall 2025")
        
        if fall_cup_questions:
            print("First few questions:")
            for i, q in enumerate(fall_cup_questions[:3]):
                print(f"  {i+1}. {q.page_url}")
                print(f"     Title: {q.question_text}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fixed_implementation())