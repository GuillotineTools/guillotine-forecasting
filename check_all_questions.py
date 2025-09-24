#!/usr/bin/env python3
"""
Script to check all open questions on Metaculus
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_all_open_questions():
    """Check all open questions on Metaculus"""
    print("Checking all open questions on Metaculus...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    try:
        # Get all open questions
        print("Fetching all open questions...")
        all_questions = MetaculusApi.get_all_open_questions()
        print(f"Found {len(all_questions)} open questions total")
        
        # Filter for questions containing "unemployment"
        unemployment_questions = [q for q in all_questions if "unemployment" in q.question_text.lower()]
        print(f"Found {len(unemployment_questions)} unemployment-related questions:")
        for q in unemployment_questions:
            print(f"  - {q.id}: {q.question_text}")
            
        # Check if the specific question (ID 39582) is in the list
        target_question = None
        for q in all_questions:
            if q.id == 39582:
                target_question = q
                break
                
        if target_question:
            print(f"\nFound target question (ID 39582):")
            print(f"  - {target_question.id}: {target_question.question_text}")
            print(f"  - In tournaments: {getattr(target_question, 'tournaments', 'Unknown')}")
        else:
            print(f"\nTarget question (ID 39582) not found in open questions")
            
    except Exception as e:
        print(f"Error checking questions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_all_open_questions()