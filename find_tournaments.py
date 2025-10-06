#!/usr/bin/env python3
"""
Find available tournaments and their correct identifiers.
"""
import asyncio
import os
import sys
from datetime import datetime

# Set up environment
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

async def find_tournaments():
    """Find available tournaments."""
    try:
        from forecasting_tools import MetaculusApi
        from forecasting_tools.helpers.metaculus_api import ApiFilter

        print("🔍 FINDING AVAILABLE TOURNAMENTS")
        print("=" * 50)

        # Get API token
        metaculus_token = os.getenv('METACULUS_TOKEN')
        if not metaculus_token:
            print("❌ METACULUS_TOKEN not set!")
            return False

        print(f"✅ Using Metaculus API")

        # Try to get current tournaments
        try:
            print(f"\n📊 Checking known tournament IDs...")

            # Try different tournament identifiers
            possible_ids = [
                "brightline-watch",
                "brightlinewatch",
                "brightline",
                "brightline-watch-2024",
                "brightline-watch-2025"
            ]

            for tournament_id in possible_ids:
                print(f"\n🔍 Trying tournament: '{tournament_id}'")
                try:
                    questions = await MetaculusApi.get_questions_matching_filter(
                        ApiFilter(
                            allowed_statuses=["open"],
                            allowed_tournaments=[tournament_id]
                        )
                    )
                    print(f"✅ SUCCESS: Found {len(questions)} open questions for '{tournament_id}'")
                    if questions:
                        print(f"📋 First question: {questions[0].question_text[:100]}...")
                        return tournament_id, questions
                except Exception as e:
                    print(f"❌ Failed: {str(e)}")

        except Exception as e:
            print(f"❌ Tournament search failed: {str(e)}")

        # Try to get all open questions and look for Brightline Watch
        print(f"\n📊 Getting all open questions to find Brightline Watch...")
        try:
            all_questions = await MetaculusApi.get_questions_matching_filter(
                ApiFilter(allowed_statuses=["open"])
            )
            print(f"✅ Found {len(all_questions)} total open questions")

            # Look for Brightline Watch in question URLs or text
            brightline_questions = []
            for q in all_questions:
                if 'brightline' in str(q.page_url).lower() or 'brightline' in str(q.question_text).lower():
                    brightline_questions.append(q)
                    print(f"🔍 Found Brightline question: {q.question_text[:80]}...")

            if brightline_questions:
                print(f"✅ Found {len(brightline_questions)} Brightline Watch questions")
                return "found_by_search", brightline_questions
            else:
                print(f"❌ No Brightline Watch questions found")

        except Exception as e:
            print(f"❌ General question search failed: {str(e)}")

        # List current known tournaments
        print(f"\n📊 Checking known current tournaments...")
        try:
            print(f"AI Competition ID: {getattr(MetaculusApi, 'CURRENT_AI_COMPETITION_ID', 'Unknown')}")
            print(f"MiniBench ID: {getattr(MetaculusApi, 'CURRENT_MINIBENCH_ID', 'Unknown')}")
        except Exception as e:
            print(f"❌ Could not get tournament IDs: {str(e)}")

        return False

    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(find_tournaments())
    if result:
        tournament_id, questions = result
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Tournament ID: {tournament_id}")
        print(f"✅ Questions found: {len(questions)}")
    else:
        print(f"\n❌ FAILED TO FIND BRIGHTLINE WATCH TOURNAMENT")
        print(f"💡 Check tournament name or use a different tournament")
    sys.exit(0 if result else 1)