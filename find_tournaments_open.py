import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def find_tournaments_with_open_questions():
    print("Finding tournaments with open questions...")
    
    # Get all open questions
    try:
        api_filter = ApiFilter(allowed_statuses=["open"])
        questions = await MetaculusApi.get_questions_matching_filter(api_filter)
        print(f"Found {len(questions)} total open questions")
        
        # Group by tournament slug
        tournament_counts = {}
        for q in questions:
            if hasattr(q, 'tournaments') and q.tournaments:
                for tournament in q.tournaments:
                    if isinstance(tournament, dict) and 'slug' in tournament:
                        slug = tournament['slug']
                    elif isinstance(tournament, str):
                        slug = tournament
                    else:
                        slug = str(tournament)
                    tournament_counts[slug] = tournament_counts.get(slug, 0) + 1
            else:
                tournament_counts['no_tournament'] = tournament_counts.get('no_tournament', 0) + 1
        
        print("\nTournaments with open questions:")
        for tournament, count in sorted(tournament_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tournament}: {count} open questions")
            
        # Let's also check some other known tournaments
        other_tournaments = [
            "metaculus-cup-2025-fall",
            "ai-2027",
            "market-pulse-25q3",
            32828,  # METACULUS_CUP_FALL_2025_ID
        ]
        
        print(f"\nChecking other known tournaments:")
        for tournament in other_tournaments:
            try:
                tournament_filter = ApiFilter(allowed_tournaments=[tournament])
                tournament_questions = await MetaculusApi.get_questions_matching_filter(tournament_filter)
                open_tournament_questions = [q for q in tournament_questions if q.state and q.state.value == "open"]
                print(f"  {tournament}: {len(tournament_questions)} total, {len(open_tournament_questions)} open")
            except Exception as e:
                print(f"  {tournament}: Error - {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(find_tournaments_with_open_questions())