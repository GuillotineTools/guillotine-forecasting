#!/usr/bin/env python3
"""
Simple test to just discover Brightline Watch tournament.
"""
import asyncio
import os

# Set up environment
os.environ['GITHUB_ACTIONS'] = 'true'

async def test_tournament_discovery():
    """Just test tournament discovery."""
    try:
        from forecasting_tools import MetaculusApi
        from forecasting_tools.helpers.metaculus_api import ApiFilter

        print("🔍 SIMPLE TOURNAMENT DISCOVERY TEST")
        print("=" * 40)

        # Check environment
        print(f"METACULUS_TOKEN configured: {'YES' if os.getenv('METACULUS_TOKEN') else 'NO'}")
        print(f"OPENROUTER_API_KEY configured: {'YES' if os.getenv('OPENROUTER_API_KEY') else 'NO'}")

        if not os.getenv('METACULUS_TOKEN'):
            print("❌ No METACULUS_TOKEN - cannot proceed")
            return False

        # Get some questions to understand structure
        print(f"\n📊 Getting sample questions...")
        questions = await MetaculusApi.get_questions_matching_filter(
            ApiFilter(allowed_statuses=["open"], number_of_questions=20)
        )
        print(f"✅ Found {len(questions)} open questions")

        # Look for Brightline questions
        brightline_questions = []
        for i, q in enumerate(questions[:5]):  # Check first 5
            print(f"\nQuestion {i+1}:")
            print(f"  Text: {q.question_text[:60]}...")
            print(f"  ID: {q.id}")
            print(f"  Type: {type(q).__name__}")

            # Check URL for brightline
            if hasattr(q, 'page_url'):
                print(f"  URL: {q.page_url}")
                if 'brightline' in str(q.page_url).lower():
                    brightline_questions.append(q)
                    print("  🎯 BRIGHTLINE WATCH QUESTION FOUND!")

            # Check tournament attributes
            for attr in ['tournament', 'tournaments', 'tournament_id']:
                if hasattr(q, attr):
                    value = getattr(q, attr)
                    print(f"  {attr}: {value}")

        if brightline_questions:
            print(f"\n🎉 FOUND {len(brightline_questions)} BRIGHTLINE QUESTIONS!")
            # Save result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"brightline_found_{timestamp}.txt", 'w') as f:
                f.write(f"Found {len(brightline_questions)} Brightline questions\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                for q in brightline_questions:
                    f.write(f"\nQuestion: {q.question_text}\n")
                    f.write(f"ID: {q.id}\n")
                    f.write(f"URL: {q.page_url}\n")
            print(f"✅ Results saved to brightline_found_{timestamp}.txt")
            return True
        else:
            print("\n❌ No Brightline questions found in sample")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    from datetime import datetime
    success = asyncio.run(test_tournament_discovery())
    if success:
        print("\n🎉 TOURNAMENT DISCOVERY SUCCESSFUL!")
    else:
        print("\n❌ TOURNAMENT DISCOVERY FAILED")
    import sys
    sys.exit(0 if success else 1)