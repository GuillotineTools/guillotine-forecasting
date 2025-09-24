#!/usr/bin/env python3
"""
Script to check the fall-aib-2025 tournament by slug using ApiFilter
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi
from forecasting_tools.helpers.metaculus_api import ApiFilter

async def check_fall_aib_by_slug():
    """Check the fall-aib-2025 tournament by slug"""
    print("Checking fall-aib-2025 tournament by slug...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    try:
        # Try to get questions from the fall-aib-2025 tournament using slug
        print("Checking fall-aib-2025 tournament by slug...")
        
        # Create a filter for the specific tournament slug
        api_filter = ApiFilter(
            statuses=["open"],
            tournaments=["fall-aib-2025"]
        )
        
        questions = await MetaculusApi.get_questions_matching_filter(api_filter)
        print(f"Found {len(questions)} questions in fall-aib-2025 tournament")
        
        # Check if our unemployment question is in this list
        unemployment_question_found = False
        for q in questions:
            if q.id_of_post == 39582:
                unemployment_question_found = True
                print(f"  -> FOUND UNEMPLOYMENT QUESTION IN fall-aib-2025!")
                print(f"  - {q.id_of_post}: {q.question_text}")
                break
        if not unemployment_question_found:
            print(f"  -> Unemployment question NOT found in fall-aib-2025")
            # Show first few questions
            for q in questions[:5]:
                print(f"  - {q.id_of_post}: {q.question_text}")
                
    except Exception as e:
        print(f"Error checking fall-aib-2025 tournament: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_fall_aib_by_slug())