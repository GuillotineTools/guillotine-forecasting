#!/usr/bin/env python3
"""
Script to check what methods are available in MetaculusApi
"""
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi

def check_metaculus_api():
    """Check what methods are available in MetaculusApi"""
    print("Checking MetaculusApi methods...")
    
    # List all attributes and methods
    methods = [attr for attr in dir(MetaculusApi) if not attr.startswith('_')]
    print("Available methods:")
    for method in methods:
        print(f"  - {method}")
        
    # Check the tournament IDs
    print("\nTournament IDs:")
    print(f"  CURRENT_AI_COMPETITION_ID: {getattr(MetaculusApi, 'CURRENT_AI_COMPETITION_ID', 'Not found')}")
    print(f"  CURRENT_MINIBENCH_ID: {getattr(MetaculusApi, 'CURRENT_MINIBENCH_ID', 'Not found')}")
    print(f"  CURRENT_METACULUS_CUP_ID: {getattr(MetaculusApi, 'CURRENT_METACULUS_CUP_ID', 'Not found')}")

if __name__ == "__main__":
    check_metaculus_api()