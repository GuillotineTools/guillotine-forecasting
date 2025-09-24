import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def examine_open_questions():
    print("Examining open questions...")
    
    # Get all open questions
    try:
        api_filter = ApiFilter(allowed_statuses=["open"])
        questions = await MetaculusApi.get_questions_matching_filter(api_filter)
        print(f"Found {len(questions)} total open questions")
        
        # Show first few questions and their tournaments
        print("\nFirst 10 open questions:")
        for i, q in enumerate(questions[:10]):
            print(f"  {i+1}. {q.page_url}")
            print(f"     Title: {q.question_text}")
            if hasattr(q, 'tournaments') and q.tournaments:
                print(f"     Tournaments: {q.tournaments}")
            else:
                print(f"     Tournaments: None")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(examine_open_questions())