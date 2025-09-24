#!/usr/bin/env python3
"""
Script to check what tournament ID corresponds to fall-aib-2025
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_fall_aib_tournament():
    """Check the fall-aib-2025 tournament"""
    print("Checking fall-aib-2025 tournament...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    # Check the AIB_FALL_2025_ID constant
    fall_aib_id = getattr(MetaculusApi, 'AIB_FALL_2025_ID', 'Not found')
    print(f"AIB_FALL_2025_ID: {fall_aib_id}")
    
    # Try to check this tournament
    if fall_aib_id != 'Not found':
        try:
            print(f"Checking Fall AIB 2025 Tournament (ID: {fall_aib_id})")
            questions = MetaculusApi.get_all_open_questions_from_tournament(fall_aib_id)
            print(f"Found {len(questions)} questions in Fall AIB 2025:")
            for q in questions[:10]:  # Show first 10
                print(f"  - {q.id}: {q.question_text}")
            if len(questions) > 10:
                print(f"  ... and {len(questions) - 10} more")
        except Exception as e:
            print(f"Error checking Fall AIB 2025 tournament: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_fall_aib_tournament()