import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def debug_tournament_fetching():
    print("Debugging tournament fetching...")
    
    # Try different combinations to see what works
    test_cases = [
        ("Empty filter", ApiFilter()),
        ("Only statuses", ApiFilter(allowed_statuses=["open"])),
        ("Only AI Comp ID", ApiFilter(allowed_tournaments=[32813])),
        ("AI Comp ID + open", ApiFilter(allowed_tournaments=[32813], allowed_statuses=["open"])),
        ("Slug + open", ApiFilter(allowed_tournaments=["fall-aib-2025"], allowed_statuses=["open"])),
        ("MiniBench + open", ApiFilter(allowed_tournaments=["minibench"], allowed_statuses=["open"])),
    ]
    
    for name, filter_obj in test_cases:
        try:
            print(f"\n{name}:")
            print(f"  Filter: {filter_obj}")
            questions = await MetaculusApi.get_questions_matching_filter(filter_obj)
            print(f"  Found {len(questions)} questions")
            if questions:
                print(f"  First question: {questions[0].page_url}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_tournament_fetching())