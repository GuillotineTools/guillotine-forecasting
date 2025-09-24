#!/usr/bin/env python3
"""
Script to check Fall AIB 2025 tournament questions
"""
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi
from forecasting_tools.helpers.metaculus_api import ApiFilter

async def check_fall_tournament():
    """Check Fall AIB 2025 tournament questions"""
    print("Checking Fall AIB 2025 tournament...")
    
    # Check by slug using ApiFilter (current approach)
    print("\n1. Checking by slug using ApiFilter:")
    try:
        api_filter = ApiFilter(
            statuses=["open"],
            tournaments=["fall-aib-2025"]
        )
        questions = await MetaculusApi.get_questions_matching_filter(api_filter)
        print(f"  -> Found {len(questions)} questions using ApiFilter")
        for q in questions[:5]:  # Show first 5
            print(f"    - {q.page_url}: {q.question_text[:50]}...")
    except Exception as e:
        print(f"  -> Error: {str(e)}")
    
    # Check by ID (if available)
    print("\n2. Checking by ID:")
    try:
        # Try the AIB_FALL_2025_ID if it exists
        if hasattr(MetaculusApi, 'AIB_FALL_2025_ID'):
            tournament_id = getattr(MetaculusApi, 'AIB_FALL_2025_ID')
            print(f"  -> AIB_FALL_2025_ID = {tournament_id}")
            questions = MetaculusApi.get_all_open_questions_from_tournament(tournament_id)
            print(f"  -> Found {len(questions)} questions using ID")
            for q in questions[:5]:  # Show first 5
                print(f"    - {q.page_url}: {q.question_text[:50]}...")
        else:
            print("  -> AIB_FALL_2025_ID not found in MetaculusApi")
    except Exception as e:
        print(f"  -> Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_fall_tournament())