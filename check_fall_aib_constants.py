#!/usr/bin/env python3
"""
Check if there's another tournament ID that works
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_all_tournament_constants_for_fall_aib():
    """Check all tournament constants to see if any work for fall-aib-2025"""
    print("Checking all tournament constants for fall-aib-2025...")
    
    # Get all attributes from MetaculusApi
    attributes = [attr for attr in dir(MetaculusApi) if not attr.startswith('_')]
    
    # Look for any attributes that might be related to fall-aib-2025
    fall_aib_related = [attr for attr in attributes if 'fall' in attr.lower() or 'aib' in attr.lower() or '2025' in attr.lower()]
    
    print("Fall/AIB/2025 related constants:")
    for attr in fall_aib_related:
        value = getattr(MetaculusApi, attr)
        print(f"  {attr}: {value}")
        
        # Try to query with this value if it's a string or int
        if isinstance(value, (str, int)):
            try:
                questions = MetaculusApi.get_all_open_questions_from_tournament(value)
                print(f"    -> Found {len(questions)} questions")
                if len(questions) > 0:
                    unemployment_found = any(q.id_of_post == 39582 for q in questions)
                    print(f"    -> Unemployment question found: {unemployment_found}")
            except Exception as e:
                print(f"    -> Error: {str(e)[:50]}...")

if __name__ == "__main__":
    check_all_tournament_constants_for_fall_aib()