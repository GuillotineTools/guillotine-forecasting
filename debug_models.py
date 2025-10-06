#!/usr/bin/env python3
"""
Debug script to check exactly what models are being used in tournament mode.
"""
import asyncio
import os
import sys
from datetime import datetime

# Set up environment to simulate GitHub Actions exactly
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

async def debug_tournament_models():
    """Debug what models are actually used in tournament mode."""
    try:
        print("🔍 DEBUGGING TOURNAMENT MODE MODEL CONFIGURATION")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Check API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY not set - using test key for debugging")
            api_key = "test_key_for_debug"
        else:
            print(f"✅ OPENROUTER_API_KEY found: {api_key[:10]}...{api_key[-4:]}")

        # Import bot configuration
        from main import FallTemplateBot2025
        from fallback_llm import create_default_fallback_llm, create_synthesis_fallback_llm, create_research_fallback_llm, create_forecasting_fallback_llm

        print("\n🤖 Creating bot with tournament configuration...")

        # Create bot exactly like main.py does
        template_bot = FallTemplateBot2025(
            research_reports_per_question=1,
            predictions_per_research_report=1,
            use_research_summary_to_forecast=False,
            publish_reports_to_metaculus=False,  # Don't actually publish
            folder_to_save_reports_to=None,
            skip_previously_forecasted_questions=False,
            llms={
                "default": create_default_fallback_llm(
                    api_key=api_key,
                    temperature=0.5,
                    timeout=60,
                    allowed_tries=2,
                ),
                "synthesizer": create_synthesis_fallback_llm(
                    api_key=api_key,
                    temperature=0.3,
                    timeout=60,
                    allowed_tries=2,
                ),
                "forecaster1": create_forecasting_fallback_llm(
                    api_key=api_key,
                    temperature=0.5,
                    timeout=60,
                    allowed_tries=2,
                ),
                "forecaster2": create_forecasting_fallback_llm(
                    api_key=api_key,
                    temperature=0.5,
                    timeout=60,
                    allowed_tries=2,
                ),
                "forecaster3": create_forecasting_fallback_llm(
                    api_key=api_key,
                    temperature=0.5,
                    timeout=60,
                    allowed_tries=2,
                ),
                "forecaster4": create_forecasting_fallback_llm(
                    api_key=api_key,
                    temperature=0.5,
                    timeout=60,
                    allowed_tries=2,
                ),
                "parser": create_default_fallback_llm(
                    api_key=api_key,
                    temperature=0.3,
                    timeout=60,
                    allowed_tries=2,
                ),
                "researcher": create_research_fallback_llm(
                    api_key=api_key,
                    temperature=0.5,
                    timeout=60,
                    allowed_tries=2,
                ),
                "summarizer": create_default_fallback_llm(
                    api_key=api_key,
                    temperature=0.5,
                    timeout=60,
                    allowed_tries=2,
                ),
            },
        )

        print("\n📋 MODEL CONFIGURATION ANALYSIS:")
        print("=" * 40)

        # Check each LLM configuration
        for role, llm in template_bot._llms.items():
            print(f"\n🔧 {role.upper()}:")
            if hasattr(llm, 'model_chain'):
                print(f"   Type: FallbackLLM")
                print(f"   Primary Model: {llm.model}")
                print(f"   Model Chain ({len(llm.model_chain)} models):")
                for i, model in enumerate(llm.model_chain, 1):
                    is_free = ":free" in model or "deepseek" in model or "glm" in model or "gemini" in model or "llama" in model
                    status = "✅ FREE" if is_free else "❌ PAID"
                    print(f"      {i}. {model} {status}")
            else:
                print(f"   Type: {type(llm).__name__}")
                print(f"   Model: {getattr(llm, 'model', 'Unknown')}")
                is_openai = "gpt" in str(getattr(llm, 'model', '')).lower()
                status = "❌ OPENAI" if is_openai else "✅ NOT OPENAI"
                print(f"   Status: {status}")

        print(f"\n🎯 CONCLUSION:")
        print("=" * 40)

        # Check if any OpenAI models are present
        openai_found = False
        for role, llm in template_bot._llms.items():
            if hasattr(llm, 'model_chain'):
                # FallbackLLM with free models
                continue
            else:
                # Direct model - check if it's OpenAI
                model_name = getattr(llm, 'model', '')
                if "gpt" in model_name.lower():
                    openai_found = True
                    print(f"❌ OPENAI MODEL DETECTED: {role} -> {model_name}")

        if not openai_found:
            print("✅ NO OPENAI MODELS DETECTED - All models are free OpenRouter models")
        else:
            print("❌ OPENAI MODELS STILL PRESENT - Configuration not fixed")

        return not openai_found

    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_tournament_models())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILURE'}: Configuration is {'correct' if success else 'broken'}")
    sys.exit(0 if success else 1)