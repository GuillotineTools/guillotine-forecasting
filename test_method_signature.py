#!/usr/bin/env python3
"""
Simple test to see how forecast_on_tournament works
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Let's look at what happens when we try to get questions the way forecast_on_tournament would
from forecasting_tools import MetaculusApi

def test_tournament_access_methods():
    """Test different ways to access tournament questions"""
    print("Testing tournament access methods...")
    
    # Method 1: Direct tournament query (what forecast_on_tournament likely uses)
    print("\nMethod 1: Direct tournament query")
    try:
        questions1 = MetaculusApi.get_all_open_questions_from_tournament("fall-aib-2025")
        print(f"  -> Found {len(questions1)} questions")
    except Exception as e:
        print(f"  -> Error: {e}")
    
    # Method 2: Let's see what parameters get_all_open_questions_from_tournament accepts
    print("\nChecking method signature...")
    import inspect
    try:
        sig = inspect.signature(MetaculusApi.get_all_open_questions_from_tournament)
        print(f"  -> Signature: {sig}")
    except Exception as e:
        print(f"  -> Error getting signature: {e}")

if __name__ == "__main__":
    test_tournament_access_methods()