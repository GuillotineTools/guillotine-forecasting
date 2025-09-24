#!/usr/bin/env python3
"""
Script to check what tournaments the unemployment question belongs to
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_question_tournaments():
    """Check what tournaments the unemployment question belongs to"""
    print("Checking question tournaments...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    try:
        # Get the unemployment question
        question_url = "https://www.metaculus.com/questions/39582/us-unemployment-rate-in-nov-2025-below-nov-2024/"
        question = MetaculusApi.get_question_by_url(question_url)
        
        print(f"Question: {question.question_text}")
        
        # Check tournament slugs
        if hasattr(question, 'tournament_slugs'):
            print(f"Tournament slugs: {question.tournament_slugs}")
        else:
            print("No tournament slugs attribute found")
            
        # Check other tournament-related attributes
        tournament_attrs = ['tournaments', 'tournament', 'project', 'projects']
        for attr in tournament_attrs:
            if hasattr(question, attr):
                print(f"{attr}: {getattr(question, attr)}")
                
    except Exception as e:
        print(f"Error checking question tournaments: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_question_tournaments()