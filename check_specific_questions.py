#!/usr/bin/env python3
"""
Script to check specific questions on Metaculus
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_specific_questions():
    """Check specific questions on Metaculus"""
    print("Checking specific questions on Metaculus...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    try:
        # Try to get the specific unemployment question by ID
        print("Fetching question ID 39582...")
        try:
            question = MetaculusApi.get_question_by_post_id(39582)
            print(f"Found question:")
            print(f"  - ID: {question.id}")
            print(f"  - Title: {question.question_text}")
            print(f"  - Status: {getattr(question, 'status', 'Unknown')}")
            print(f"  - Tournament: {getattr(question, 'tournaments', 'Unknown')}")
        except Exception as e:
            print(f"Could not fetch question 39582: {e}")
            
        # Try to get questions from the tournaments
        print(f"\nChecking AI Competition Tournament (ID: {MetaculusApi.CURRENT_AI_COMPETITION_ID})")
        try:
            ai_questions = MetaculusApi.get_all_open_questions_from_tournament(
                MetaculusApi.CURRENT_AI_COMPETITION_ID
            )
            print(f"Found {len(ai_questions)} questions in AI Competition:")
            for q in ai_questions[:5]:  # Show first 5
                print(f"  - {q.id}: {q.question_text}")
            if len(ai_questions) > 5:
                print(f"  ... and {len(ai_questions) - 5} more")
        except Exception as e:
            print(f"Error checking AI Competition: {e}")
            
        print(f"\nChecking MiniBench Tournament (ID: {MetaculusApi.CURRENT_MINIBENCH_ID})")
        try:
            mini_questions = MetaculusApi.get_all_open_questions_from_tournament(
                MetaculusApi.CURRENT_MINIBENCH_ID
            )
            print(f"Found {len(mini_questions)} questions in MiniBench:")
            for q in mini_questions[:5]:  # Show first 5
                print(f"  - {q.id}: {q.question_text}")
            if len(mini_questions) > 5:
                print(f"  ... and {len(mini_questions) - 5} more")
        except Exception as e:
            print(f"Error checking MiniBench: {e}")
            
    except Exception as e:
        print(f"Error checking questions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_specific_questions()