#!/usr/bin/env python3
"""
Test script to verify the bot will forecast on the unemployment question
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi
from forecasting_tools.helpers.metaculus_api import ApiFilter

async def test_unemployment_question():
    """Test that we can get the unemployment question and that the bot would forecast on it"""
    print("Testing unemployment question access...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    try:
        # Get the unemployment question directly
        print("Getting unemployment question directly...")
        question_url = "https://www.metaculus.com/questions/39582/us-unemployment-rate-in-nov-2025-below-nov-2024/"
        question = MetaculusApi.get_question_by_url(question_url)
        print(f"SUCCESS: Successfully got question: {question.question_text}")
        print(f"  - ID: {question.id_of_post}")
        print(f"  - Tournament slugs: {question.tournament_slugs}")
        
        # Get questions from fall-aib-2025 tournament
        print("\nGetting questions from fall-aib-2025 tournament...")
        api_filter = ApiFilter(
            statuses=["open"],
            tournaments=["fall-aib-2025"]
        )
        questions = await MetaculusApi.get_questions_matching_filter(api_filter)
        print(f"SUCCESS: Found {len(questions)} questions in fall-aib-2025 tournament")
        
        # Check if our question is in this list
        unemployment_question_found = False
        for q in questions:
            if q.id_of_post == 39582:
                unemployment_question_found = True
                print(f"SUCCESS: Found unemployment question in tournament:")
                print(f"  - {q.id_of_post}: {q.question_text}")
                break
        
        if not unemployment_question_found:
            print("ERROR: Unemployment question NOT found in fall-aib-2025 tournament")
            return False
            
        print("\nSUCCESS: All tests passed! The bot should now be able to forecast on this question.")
        return True
        
    except Exception as e:
        print(f"ERROR: Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_unemployment_question())
    exit(0 if success else 1)