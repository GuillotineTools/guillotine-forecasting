import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def debug_tournament_without_status():
    print("Debugging tournament fetching without status filter...")
    
    # Try different combinations without status filter
    test_cases = [
        ("AI Comp ID only", ApiFilter(allowed_tournaments=[32813])),
        ("Slug only", ApiFilter(allowed_tournaments=["fall-aib-2025"])),
        ("MiniBench only", ApiFilter(allowed_tournaments=["minibench"])),
    ]
    
    for name, filter_obj in test_cases:
        try:
            print(f"\n{name}:")
            print(f"  Filter: {filter_obj}")
            questions = await MetaculusApi.get_questions_matching_filter(filter_obj)
            print(f"  Found {len(questions)} questions")
            if questions:
                # Check if they're actually from the right tournament and are open
                open_questions = [q for q in questions if q.state and q.state.value == "open"]
                print(f"  Open questions: {len(open_questions)}")
                if open_questions:
                    print(f"  First open question: {open_questions[0].page_url}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_tournament_without_status())