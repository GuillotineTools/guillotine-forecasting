#!/usr/bin/env python3
"""
Simple script to find the Brightline Watch tournament ID.
"""
import asyncio
import os
from datetime import datetime

# Set up environment
os.environ['GITHUB_ACTIONS'] = 'true'

async def find_tournament():
    """Find Brightline Watch tournament ID."""
    try:
        from forecasting_tools import MetaculusApi
        from forecasting_tools.helpers.metaculus_api import ApiFilter

        print("🔍 FINDING BRIGHTLINE WATCH TOURNAMENT ID")
        print("=" * 50)

        # Get API token
        metaculus_token = os.getenv('METACULUS_TOKEN')
        if not metaculus_token:
            print("❌ METACULUS_TOKEN not set!")
            return False

        print(f"✅ Metaculus API configured")

        # Get all open questions and look for Brightline Watch
        print(f"\n📊 Getting open questions to find Brightline Watch...")
        all_questions = await MetaculusApi.get_questions_matching_filter(
            ApiFilter(allowed_statuses=["open"], number_of_questions=100)
        )
        print(f"✅ Found {len(all_questions)} total open questions")

        # Look for Brightline Watch questions
        brightline_questions = []
        tournament_ids = set()

        for q in all_questions:
            if hasattr(q, 'page_url') and 'brightline' in str(q.page_url).lower():
                brightline_questions.append(q)
                print(f"🎯 Found Brightline question: {q.question_text[:80]}...")
                print(f"   URL: {q.page_url}")

                # Check tournament attributes
                if hasattr(q, 'tournament') and q.tournament:
                    tournament_ids.add(q.tournament)
                    print(f"   📋 Tournament ID: {q.tournament}")
                elif hasattr(q, 'tournaments') and q.tournaments:
                    for t in q.tournaments:
                        tournament_ids.add(t)
                    print(f"   📋 Tournaments: {q.tournaments}")

                # Show all available attributes
                attrs = [attr for attr in dir(q) if not attr.startswith('_')]
                print(f"   🔍 Available attributes: {attrs[:10]}...")

        if tournament_ids:
            print(f"\n🎉 FOUND TOURNAMENT IDs: {list(tournament_ids)}")

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"brightline_tournament_info_{timestamp}.md", 'w') as f:
                f.write(f"# Brightline Watch Tournament Information\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Total Brightline Questions Found:** {len(brightline_questions)}\n")
                f.write(f"**Tournament IDs:** {list(tournament_ids)}\n\n")

                f.write(f"## Questions Found:\n\n")
                for i, q in enumerate(brightline_questions, 1):
                    f.write(f"### Question {i}\n")
                    f.write(f"**ID:** {q.id if hasattr(q, 'id') else 'Unknown'}\n")
                    f.write(f"**Text:** {q.question_text}\n")
                    f.write(f"**URL:** {q.page_url}\n")
                    if hasattr(q, 'tournament') and q.tournament:
                        f.write(f"**Tournament:** {q.tournament}\n")
                    elif hasattr(q, 'tournaments') and q.tournaments:
                        f.write(f"**Tournaments:** {q.tournaments}\n")
                    f.write(f"\n")

            print(f"✅ Results saved to brightline_tournament_info_{timestamp}.md")
            return True
        else:
            print("❌ No tournament IDs found")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(find_tournament())
    if success:
        print("\n🎉 BRIGHTLINE WATCH TOURNAMENT FOUND!")
    else:
        print("\n❌ FAILED TO FIND TOURNAMENT")
    import sys
    sys.exit(0 if success else 1)