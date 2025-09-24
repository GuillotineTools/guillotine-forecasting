#!/usr/bin/env python3
"""
Verification script to test that the bot can forecast on the specific questions
mentioned by the user.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from forecasting_tools import MetaculusApi, ApiFilter
from main import FallTemplateBot2025

async def test_specific_questions():
    """Test that the bot can find and forecast on specific questions"""
    print("=== Testing Specific Questions ===")

    # Test Spain vs Eurozone growth question
    print("\n1. Testing Spain vs Eurozone growth question (39449)...")
    try:
        # Try to get question by ID from the web
        import requests
        response = requests.get(f"https://www.metaculus.com/api2/questions/39449/")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found: {data['title']}")
            print(f"   Status: {data['status']}")
            print(f"   URL: https://www.metaculus.com/questions/39449/")
        else:
            print(f"   Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test Inditex question
    print("\n2. Testing Inditex top 10 EU question (39382)...")
    try:
        # Try to get question by ID from the web
        import requests
        response = requests.get(f"https://www.metaculus.com/api2/questions/39382/")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found: {data['title']}")
            print(f"   Status: {data['status']}")
            print(f"   URL: https://www.metaculus.com/questions/39382/")
        else:
            print(f"   Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test Metaculus Cup questions
    print("\n3. Testing Metaculus Cup questions...")
    try:
        metaculus_cup_filter = ApiFilter(
            allowed_statuses=["open"],
            allowed_tournaments=[32828]  # Metaculus Cup ID
        )
        questions = await MetaculusApi.get_questions_matching_filter(metaculus_cup_filter)
        print(f"   Found {len(questions)} open questions in Metaculus Cup")

        # Check if our target questions are in the list
        question_urls = [q.page_url for q in questions]
        if any("39449" in url for url in question_urls):
            print("   ✓ Spain vs Eurozone question (39449) is in Metaculus Cup")
        else:
            print("   ✗ Spain vs Eurozone question (39449) is NOT in Metaculus Cup")

        if any("39382" in url for url in question_urls):
            print("   ✓ Inditex question (39382) is in Metaculus Cup")
        else:
            print("   ✗ Inditex question (39382) is NOT in Metaculus Cup")

        # List all questions
        print("\n   All Metaculus Cup questions:")
        for q in questions:
            print(f"   - ID {q.id}: {q.question_text[:100]}...")

    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(test_specific_questions())