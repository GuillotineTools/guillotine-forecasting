#!/usr/bin/env python3
"""
Debug script to check Market Pulse tournament questions
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi
from forecasting_tools.helpers.metaculus_api import ApiFilter

async def debug_market_pulse():
    print("🔍 Debugging Market Pulse tournament...")
    
    # Check if we have API token
    if not os.getenv('METACULUS_TOKEN'):
        print("❌ METACULUS_TOKEN not set. Cannot fetch live data.")
        return
    
    try:
        print(f"\n📋 Using Market Pulse tournament ID: {MetaculusApi.CURRENT_MARKET_PULSE_ID}")
        
        # Try to get Market Pulse questions
        market_pulse_filter = ApiFilter(
            allowed_statuses=["open"],
            allowed_tournaments=[MetaculusApi.CURRENT_MARKET_PULSE_ID]
        )
        market_pulse_questions = await MetaculusApi.get_questions_matching_filter(market_pulse_filter)
        
        print(f"\n📊 Found {len(market_pulse_questions)} open Market Pulse questions:")
        
        for i, q in enumerate(market_pulse_questions, 1):
            print(f"\n{i}. {q.question_text}")
            print(f"   URL: {q.page_url}")
            print(f"   Type: {getattr(q.question_type, 'value', 'unknown')}")
            print(f"   Status: {getattr(q, 'state.name', 'unknown')}")
            print(f"   Tournaments: {getattr(q, 'tournaments', 'unknown')}")
            print(f"   Projects: {getattr(q, 'projects', 'unknown')}")
        
        # Also get all Market Pulse questions (including closed)
        print(f"\n🔍 Checking all Market Pulse questions (including closed)...")
        all_market_pulse_filter = ApiFilter(
            allowed_tournaments=[MetaculusApi.CURRENT_MARKET_PULSE_ID]
        )
        all_market_pulse_questions = await MetaculusApi.get_questions_matching_filter(all_market_pulse_filter)
        print(f"Total Market Pulse questions: {len(all_market_pulse_questions)}")
        
        # If no questions found, try keyword search
        if len(market_pulse_questions) == 0:
            print(f"\n🔍 No open Market Pulse questions found via tournament filter.")
            print(f"Trying keyword search in all open questions...")
            
            all_open_filter = ApiFilter(allowed_statuses=["open"])
            all_open_questions = await MetaculusApi.get_questions_matching_filter(all_open_filter)
            
            market_pulse_keywords = [
                'S&P 500', 'stock market', 'Market Pulse', 'market index', 
                'trading', 'financial markets', 'equity markets', 'volatility',
                'NYSE', 'NASDAQ', 'Dow Jones'
            ]
            
            found_questions = []
            for q in all_open_questions:
                if hasattr(q, 'question_text'):
                    question_text_lower = q.question_text.lower()
                    if any(keyword.lower() in question_text_lower for keyword in market_pulse_keywords):
                        found_questions.append(q)
            
            print(f"Found {len(found_questions)} potential Market Pulse questions by keyword:")
            for i, q in enumerate(found_questions, 1):
                print(f"\n{i}. {q.question_text}")
                print(f"   URL: {q.page_url}")
                print(f"   Type: {getattr(q.question_type, 'value', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_market_pulse())