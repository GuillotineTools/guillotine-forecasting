#!/usr/bin/env python3
"""
Test BinaryQuestion object attributes to find the correct way to get question ID.
"""

import os
import asyncio

os.environ['GITHUB_ACTIONS'] = 'true'

async def test_binary_question_attributes():
    print("🔍 TESTING BINARY QUESTION ATTRIBUTES")
    print("=" * 50)

    metaculus_token = os.getenv('METACULUS_TOKEN')
    if not metaculus_token:
        print("❌ Need METACULUS_TOKEN")
        return False

    try:
        from forecasting_tools import MetaculusApi

        print("🔄 Getting Bondi question...")
        bondi_question = await MetaculusApi.get_question_by_url("https://www.metaculus.com/questions/39988/")

        print(f"✅ Got question: {bondi_question.question_text[:60]}...")
        print(f"   Type: {type(bondi_question).__name__}")

        # List all available attributes
        print("\n📋 AVAILABLE ATTRIBUTES:")
        attrs = [attr for attr in dir(bondi_question) if not attr.startswith('_')]
        for attr in sorted(attrs):
            try:
                value = getattr(bondi_question, attr)
                print(f"   {attr}: {type(value).__name__} = {str(value)[:50]}...")
            except Exception as e:
                print(f"   {attr}: ERROR - {e}")

        # Look specifically for ID-like attributes
        print("\n🎯 LOOKING FOR ID ATTRIBUTES:")
        id_attrs = ['id', 'question_id', 'question', 'num', 'number']
        for attr in id_attrs:
            if hasattr(bondi_question, attr):
                value = getattr(bondi_question, attr)
                print(f"   ✅ {attr}: {value} ({type(value).__name__})")
            else:
                print(f"   ❌ {attr}: Not found")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_binary_question_attributes())
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")