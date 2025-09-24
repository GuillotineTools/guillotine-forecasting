import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def test_working_method_parameters():
    print("Testing what parameters work...")
    
    # This is what worked before (but with incorrect parameter names)
    try:
        print("\n1. Using the parameters that worked before (manually)...")
        # Create the filter with the parameters exactly as they would be passed to the API
        # But we need to figure out what parameters were actually being used
        
        # Let's try to recreate what happened in our first successful test
        # In that test, we used:
        # api_filter = ApiFilter(
        #     statuses=["open"],
        #     tournaments=["fall-aib-2025"]
        # )
        # But these aren't valid ApiFilter parameters!
        
        # Let's see what happens when we create an empty filter
        api_filter1 = ApiFilter()
        print(f"Empty ApiFilter: {api_filter1}")
        questions1 = await MetaculusApi.get_questions_matching_filter(api_filter1)
        print(f"Found {len(questions1)} questions with empty filter")
        for q in questions1[:3]:  # Just show first 3
            print(f"  - {q.page_url}: {q.question_text}")
            
    except Exception as e:
        print(f"Error with empty filter: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_working_method_parameters())