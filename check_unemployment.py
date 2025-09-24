#!/usr/bin/env python3
"""
Script to check the unemployment question specifically
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_unemployment_question():
    """Check the unemployment question specifically"""
    print("Checking unemployment question...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    try:
        # Try to get the specific unemployment question by URL
        print("Fetching question by URL...")
        question_url = "https://www.metaculus.com/questions/39582/us-unemployment-rate-in-nov-2025-below-nov-2024/"
        question = MetaculusApi.get_question_by_url(question_url)
        print(f"Found question:")
        print(f"  - Type: {type(question)}")
        print(f"  - Attributes: {[attr for attr in dir(question) if not attr.startswith('_')]}")
        
        # Print some key attributes
        if hasattr(question, 'page_url'):
            print(f"  - URL: {question.page_url}")
        if hasattr(question, 'question_text'):
            print(f"  - Text: {question.question_text}")
            
    except Exception as e:
        print(f"Error checking question: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_unemployment_question()