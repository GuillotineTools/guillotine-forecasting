#!/usr/bin/env python3
"""
Script to test forecast_on_tournament method directly
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import MetaculusApi
from main import FallTemplateBot2025
from forecasting_tools import GeneralLlm

def test_forecast_on_tournament():
    """Test forecast_on_tournament method directly"""
    print("Testing forecast_on_tournament method...")
    
    # Check if we have the required token
    if not os.getenv('METACULUS_TOKEN'):
        print("ERROR: METACULUS_TOKEN not set")
        return
    
    try:
        # Create a minimal bot instance
        template_bot = FallTemplateBot2025(
            research_reports_per_question=1,
            predictions_per_research_report=1,
            use_research_summary_to_forecast=False,
            publish_reports_to_metaculus=False,  # Don't actually publish
            folder_to_save_reports_to=None,
            skip_previously_forecasted_questions=True,
            llms={
                "default": GeneralLlm(
                    model="openrouter/openai/gpt-4o-mini",
                    temperature=0.5,
                    timeout=60,
                    allowed_tries=2,
                ),
                "synthesizer": GeneralLlm(
                    model="openrouter/openai/gpt-4o-mini",
                    temperature=0.3,
                    timeout=60,
                    allowed_tries=2,
                ),
                "forecaster1": "openrouter/openai/gpt-4o-mini",
                "forecaster2": "openrouter/openai/gpt-4o-mini",
                "parser": "openrouter/openai/gpt-4o-mini",
                "researcher": "openrouter/openai/gpt-4o-mini",
                "summarizer": "openrouter/openai/gpt-4o-mini",
            },
        )
        
        # Test with different tournament identifiers
        identifiers = [
            "fall-aib-2025",
            32813,
            "32813"
        ]
        
        for identifier in identifiers:
            print(f"\nTesting forecast_on_tournament with identifier: {identifier}")
            try:
                reports = asyncio.run(
                    template_bot.forecast_on_tournament(identifier, return_exceptions=True)
                )
                print(f"  -> Generated {len(reports)} forecast reports")
            except Exception as e:
                print(f"  -> Error: {str(e)[:100]}...")
                
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_forecast_on_tournament()