#!/usr/bin/env python3
"""
Script to check if the unemployment question is in ACX or AI_2027 tournaments
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_acx_and_ai2027():
    """Check if the unemployment question is in ACX or AI_2027 tournaments"""
    print("Checking ACX and AI_2027 tournaments...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    # Get the unemployment question to check its tournament
    try:
        question_url = "https://www.metaculus.com/questions/39582/us-unemployment-rate-in-nov-2025-below-nov-2024/"
        question = MetaculusApi.get_question_by_url(question_url)
        print(f"Question: {question.question_text}")
        print(f"Tournament slugs: {question.tournament_slugs}")
        print(f"Question ID: {question.id_of_post}")  # Use correct attribute
    except Exception as e:
        print(f"Error getting question: {e}")
        return
    
    # Check ACX_2025_TOURNAMENT (ID: 32564)
    try:
        print(f"\nChecking ACX 2025 Tournament (ID: 32564)")
        questions = MetaculusApi.get_all_open_questions_from_tournament(32564)
        print(f"Found {len(questions)} questions in ACX 2025")
        
        # Check if our question is in this tournament
        unemployment_question_found = False
        for q in questions:
            if q.id_of_post == 39582:
                unemployment_question_found = True
                print(f"  -> FOUND UNEMPLOYMENT QUESTION IN ACX 2025!")
                break
        if not unemployment_question_found:
            print(f"  -> Unemployment question NOT found in ACX 2025")
            
    except Exception as e:
        print(f"Error checking ACX 2025 tournament: {e}")
    
    # Check AI_2027_TOURNAMENT_ID (ID: ai-2027)
    try:
        print(f"\nChecking AI 2027 Tournament (ID: ai-2027)")
        questions = MetaculusApi.get_all_open_questions_from_tournament("ai-2027")
        print(f"Found {len(questions)} questions in AI 2027")
        
        # Check if our question is in this tournament
        unemployment_question_found = False
        for q in questions:
            if q.id_of_post == 39582:
                unemployment_question_found = True
                print(f"  -> FOUND UNEMPLOYMENT QUESTION IN AI 2027!")
                break
        if not unemployment_question_found:
            print(f"  -> Unemployment question NOT found in AI 2027")
            
    except Exception as e:
        print(f"Error checking AI 2027 tournament: {e}")

if __name__ == "__main__":
    check_acx_and_ai2027()