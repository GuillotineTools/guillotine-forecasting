#!/usr/bin/env python3
"""
Test the Metaculus Cup with the new ID
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def test_metaculus_cup_new_id():
    """Test the Metaculus Cup with the new ID 32828"""
    print("Testing Metaculus Cup with new ID 32828...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    try:
        # Test with the new ID
        print("Checking Metaculus Cup Tournament (ID: 32828)")
        questions = MetaculusApi.get_all_open_questions_from_tournament(32828)
        print(f"Found {len(questions)} questions in Metaculus Cup:")
        for q in questions[:5]:  # Show first 5
            print(f"  - {q.id_of_post}: {q.question_text}")
        if len(questions) > 5:
            print(f"  ... and {len(questions) - 5} more")
            
    except Exception as e:
        print(f"Error checking Metaculus Cup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metaculus_cup_new_id()