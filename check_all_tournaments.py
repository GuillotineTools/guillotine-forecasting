#!/usr/bin/env python3
"""
Script to check all tournament constants
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_all_tournament_constants():
    """Check all tournament constants"""
    print("Checking all tournament constants...")
    
    # List all tournament-related constants
    tournament_constants = [
        'CURRENT_AI_COMPETITION_ID',
        'AIB_FALL_2025_ID',
        'CURRENT_MINIBENCH_ID',
        'CURRENT_METACULUS_CUP_ID',
        'CURRENT_QUARTERLY_CUP_ID',
        'METACULUS_CUP_2025_1_ID',
        'ACX_2025_TOURNAMENT',
        'AI_2027_TOURNAMENT_ID',
        'Q1_2025_QUARTERLY_CUP',
        'Q3_2024_QUARTERLY_CUP',
        'Q4_2024_QUARTERLY_CUP',
        'AI_COMPETITION_ID_Q1',
        'AI_COMPETITION_ID_Q2',
        'AI_COMPETITION_ID_Q3',
        'AI_COMPETITION_ID_Q4',
        'AI_WARMUP_TOURNAMENT_ID',
        'PRO_COMPARISON_TOURNAMENT_Q1',
        'PRO_COMPARISON_TOURNAMENT_Q2'
    ]
    
    for constant in tournament_constants:
        value = getattr(MetaculusApi, constant, 'Not found')
        print(f"{constant}: {value}")
        
        # Try to check this tournament if it exists
        if value != 'Not found' and isinstance(value, (str, int)):
            try:
                questions = MetaculusApi.get_all_open_questions_from_tournament(value)
                print(f"  -> Found {len(questions)} questions")
            except Exception as e:
                print(f"  -> Error: {str(e)[:100]}...")

if __name__ == "__main__":
    check_all_tournament_constants()