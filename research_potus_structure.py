#!/usr/bin/env python3
"""
Research POTUS question structure to understand proper discovery method.
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def research_potus_structure():
    """Research the POTUS question structure."""
    try:
        from forecasting_tools import MetaculusApi, ApiFilter

        print("🔍 RESEARCHING POTUS QUESTION STRUCTURE")
        print("=" * 50)

        # Check API key
        if not os.getenv('METACULUS_TOKEN'):
            print("❌ METACULUS_TOKEN not set")
            return

        print("✅ METACULUS_TOKEN configured")

        # Method 1: Try to get the specific POTUS question by ID
        print("\n📋 METHOD 1: Direct question access")
        try:
            question = await MetaculusApi.get_question_by_post_id(39988)
            print(f"✅ Found question: {question.question_text[:80]}...")
            print(f"   Type: {type(question).__name__}")
            print(f"   URL: {question.page_url}")

            # Check all attributes for tournament/series info
            print(f"   Available attributes: {[attr for attr in dir(question) if not attr.startswith('_') and not callable(getattr(question, attr))]}")

            # Check specific attributes that might contain tournament info
            for attr in ['tournament', 'tournaments', 'series', 'community', 'category', 'group']:
                if hasattr(question, attr):
                    value = getattr(question, attr)
                    print(f"   {attr}: {value}")

        except Exception as e:
            print(f"❌ Direct access failed: {e}")

        # Method 2: Search with different filters
        print("\n📋 METHOD 2: Filter search experiments")

        # Try different search terms in question text
        search_terms = ["POTUS", "President", "Bondi", "Attorney General", "Trump", "Cabinet"]

        for term in search_terms:
            try:
                print(f"\n   Searching for questions with '{term}'...")

                # Try text search through general questions
                api_filter = ApiFilter(
                    statuses=["open"],
                    number_of_questions=50
                )

                questions = await MetaculusApi.get_questions_matching_filter(api_filter)

                matching_questions = []
                for q in questions:
                    if term.lower() in q.question_text.lower():
                        matching_questions.append(q)

                if matching_questions:
                    print(f"   ✅ Found {len(matching_questions)} questions with '{term}'")
                    for q in matching_questions[:3]:  # Show first 3
                        print(f"      - {q.question_text[:60]}...")
                        print(f"        URL: {q.page_url}")
                        if hasattr(q, 'tournament'):
                            print(f"        Tournament: {q.tournament}")
                        if hasattr(q, 'tournaments') and q.tournaments:
                            print(f"        Tournaments: {q.tournaments}")
                else:
                    print(f"   ❌ No questions found with '{term}'")

            except Exception as e:
                print(f"   ❌ Search for '{term}' failed: {e}")

        # Method 3: Check all possible tournament/series slugs
        print("\n📋 METHOD 3: Tournament slug experiments")

        possible_tournaments = [
            "potus", "potus-predictions", "potus-2024", "potus-2025",
            "president", "presidential", "elections", "politics",
            "us-politics", "american-politics", "cabinet", "executive"
        ]

        for tournament_slug in possible_tournaments:
            try:
                print(f"\n   Trying tournament slug '{tournament_slug}'...")

                api_filter = ApiFilter(
                    statuses=["open"],
                    tournaments=[tournament_slug],
                    number_of_questions=10
                )

                questions = await MetaculusApi.get_questions_matching_filter(api_filter)

                if questions:
                    print(f"   ✅ Found {len(questions)} questions in '{tournament_slug}'")
                    for q in questions[:2]:  # Show first 2
                        print(f"      - {q.question_text[:60]}...")
                        print(f"        URL: {q.page_url}")
                else:
                    print(f"   ❌ No questions found in '{tournament_slug}'")

            except Exception as e:
                print(f"   ❌ Tournament '{tournament_slug}' failed: {e}")

        # Method 4: Try community-based search
        print("\n📋 METHOD 4: Community/category experiments")

        # Check if there are community endpoints
        try:
            print("   Checking if question has community info...")
            question = await MetaculusApi.get_question_by_post_id(39988)

            # Check if page_url contains community info
            if "/c/" in question.page_url:
                community_slug = question.page_url.split("/c/")[1].split("/")[0]
                print(f"   Found community slug: {community_slug}")

                # Try to search this community
                api_filter = ApiFilter(
                    statuses=["open"],
                    communities=[community_slug],
                    number_of_questions=10
                )

                community_questions = await MetaculusApi.get_questions_matching_filter(api_filter)
                print(f"   ✅ Found {len(community_questions)} questions in community '{community_slug}'")

            else:
                print("   ❌ No community info found in page URL")

        except Exception as e:
            print(f"   ❌ Community search failed: {e}")

    except Exception as e:
        print(f"❌ Research failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(research_potus_structure())