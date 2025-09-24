#!/usr/bin/env python3
"""
Script to check all possible ways to query the fall-aib-2025 tournament
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_all_tournament_query_methods():
    """Check all possible ways to query the fall-aib-2025 tournament"""
    print("Checking all tournament query methods...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    # List of possible tournament identifiers to try
    tournament_identifiers = [
        "fall-aib-2025",  # The slug
        32813,            # AIB_FALL_2025_ID
        "32813",          # String version of ID
        "Fall 2025 AI Forecasting Benchmark tournament",  # Full name
        "fall 2025 ai forecasting benchmark tournament",  # Lowercase
    ]
    
    for identifier in tournament_identifiers:
        try:
            print(f"\nTrying identifier: {identifier} (type: {type(identifier).__name__})")
            questions = MetaculusApi.get_all_open_questions_from_tournament(identifier)
            print(f"  -> Found {len(questions)} questions")
            
            # Check if unemployment question is in the results
            unemployment_found = any(q.id_of_post == 39582 for q in questions)
            print(f"  -> Unemployment question found: {unemployment_found}")
            
        except Exception as e:
            print(f"  -> Error: {str(e)[:100]}...")

if __name__ == "__main__":
    check_all_tournament_query_methods()