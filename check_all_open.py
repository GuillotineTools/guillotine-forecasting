import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools.helpers.metaculus_api import MetaculusApi, ApiFilter

async def check_all_open_questions():
    print("Checking all open questions...")
    
    # Get all open questions regardless of tournament
    try:
        api_filter = ApiFilter(allowed_statuses=["open"])
        questions = await MetaculusApi.get_questions_matching_filter(api_filter)
        print(f"Found {len(questions)} total open questions")
        
        # Group by tournament
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
        
        print("\nOpen questions by tournament:")
        for tournament, count in sorted(tournament_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tournament}: {count}")
            
        # Check specifically for our target tournaments
        target_tournaments = ['fall-aib-2025', 'minibench']
        print(f"\nChecking specific target tournaments:")
        for target in target_tournaments:
            target_filter = ApiFilter(allowed_tournaments=[target])
            target_questions = await MetaculusApi.get_questions_matching_filter(target_filter)
            open_target_questions = [q for q in target_questions if q.state and q.state.value == "open"]
            print(f"  {target}: {len(target_questions)} total, {len(open_target_questions)} open")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_all_open_questions())