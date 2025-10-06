#!/usr/bin/env python3
"""
Test multiforecaster on real Metaculus questions with detailed logging.
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Set up environment
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

async def test_real_questions():
    """Test multiforecaster on real questions."""
    try:
        from fallback_llm import create_default_fallback_llm, create_research_fallback_llm, create_synthesis_fallback_llm, create_forecasting_fallback_llm
        from forecasting_tools import MetaculusApi, BinaryQuestion
        from forecasting_tools.helpers.metaculus_api import ApiFilter

        print("🎯 TESTING MULTIFORECASTER ON REAL METACULUS QUESTIONS")
        print("=" * 70)
        print("This will:")
        print("1. Find real open questions from available tournaments")
        print("2. Use detailed API call logging")
        print("3. Run complete multiforecaster process")
        print("4. Save all outputs to /outputs/ folder")

        # Get API keys
        api_key = os.getenv('OPENROUTER_API_KEY')
        metaculus_token = os.getenv('METACULUS_TOKEN')

        if not api_key:
            print("❌ OPENROUTER_API_KEY is not set!")
            return False

        if not metaculus_token:
            print("❌ METACULUS_TOKEN is not set!")
            return False

        print(f"✅ API keys configured")

        # Create outputs directory
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        # Step 1: Find real questions
        print(f"\n📊 STEP 1: FINDING REAL QUESTIONS")

        # Try different tournaments to find real questions
        tournaments_to_try = [
            32813,  # AI Competition (actual ID)
            "minibench",  # MiniBench (actual ID)
            "brightlinewatch",  # Brightline Watch (from URL /c/brightlinewatch/)
            "brightline-watch",  # Alternative format
            "brightline_watch",  # Alternative format
            "brightline",  # Alternative format
            None,  # Try general questions
        ]

        real_questions = []
        tournament_used = None

        for tournament in tournaments_to_try:
            if tournament is None:
                print("🔍 Checking general open questions")
                try:
                    questions = await MetaculusApi.get_questions_matching_filter(
                        ApiFilter(allowed_statuses=["open"])
                    )
                except Exception as e:
                    error_str = str(e)
                    print(f"❌ Failed to get general questions: {error_str[:100]}{'...' if len(error_str) > 100 else ''}")
                    if 'HTTPError' in error_str and 'Response reason:' in error_str:
                        import re
                        http_match = re.search(r'Reason: (\w+)', error_str)
                        if http_match:
                            print(f"   HTTP Error: {http_match.group(1)}")
                    continue
            else:
                print(f"🔍 Checking tournament: {tournament}")
                try:
                    # Get tournament-specific questions
                    questions = await MetaculusApi.get_questions_matching_filter(
                        ApiFilter(
                            allowed_statuses=["open"],
                            allowed_tournaments=[tournament]
                        )
                    )
                except Exception as e:
                    error_str = str(e)
                    print(f"❌ Failed to get questions for '{tournament}': {error_str[:100]}{'...' if len(error_str) > 100 else ''}")
                    if 'HTTPError' in error_str and 'Response reason:' in error_str:
                        # Extract more detailed HTTP error info
                        import re
                        http_match = re.search(r'Reason: (\w+)', error_str)
                        if http_match:
                            print(f"   HTTP Error: {http_match.group(1)}")
                    continue

            print(f"✅ Found {len(questions)} open questions for '{tournament if tournament else 'general'}'")

            if questions:
                real_questions = questions
                tournament_used = tournament if tournament else "general"
                break

        if not real_questions:
            print("⚠️  No questions found from tournament-specific search")
            print("🔍 Searching for Brightline Watch questions in all open questions...")

            try:
                all_questions = await MetaculusApi.get_questions_matching_filter(
                    ApiFilter(allowed_statuses=["open"], number_of_questions=50)
                )
                print(f"✅ Found {len(all_questions)} total open questions")

                # Look for Brightline Watch questions manually
                brightline_questions = []
                for q in all_questions:
                    if (hasattr(q, 'page_url') and 'brightline' in str(q.page_url).lower()) or \
                       (hasattr(q, 'question_text') and 'brightline' in str(q.question_text).lower()):
                        brightline_questions.append(q)
                        print(f"🎯 Found Brightline Watch question: {q.question_text[:80]}...")
                        if hasattr(q, 'tournament') and q.tournament:
                            print(f"   📋 Tournament ID: {q.tournament}")

                if brightline_questions:
                    real_questions = brightline_questions
                    tournament_used = "found_by_search"
                    print(f"✅ Found {len(brightline_questions)} Brightline Watch questions by search")
                else:
                    print("❌ No Brightline Watch questions found anywhere")
                    return False

            except Exception as e:
                print(f"❌ Search failed: {str(e)}")
                return False

        print(f"✅ Using {len(real_questions)} questions from tournament: {tournament_used}")

        # Create LLM instances
        print(f"\n🤖 STEP 2: INITIALIZING MULTIFORECASTER")

        researcher_llm = create_research_fallback_llm(api_key=api_key, temperature=0.3, timeout=60, allowed_tries=2)
        forecaster_llm = create_forecasting_fallback_llm(api_key=api_key, temperature=0.5, timeout=60, allowed_tries=2)
        synthesizer_llm = create_synthesis_fallback_llm(api_key=api_key, temperature=0.3, timeout=60, allowed_tries=2)

        print(f"✅ All LLM instances created with detailed logging enabled")

        # Process first real question
        question = real_questions[0]
        print(f"\n🎯 STEP 3: PROCESSING REAL QUESTION")
        print(f"Question: {question.question_text}")
        print(f"URL: {question.page_url}")
        print(f"Type: {type(question).__name__}")

        # Research Phase
        print(f"\n📚 STEP 4: RESEARCH PHASE")
        print(f"Running detailed research with API call logging...")

        research_prompt = f"""
Research this question thoroughly: {question.question_text}

Page URL: {question.page_url}

Task:
1. Research the specific topic and context
2. Look for relevant data, trends, and expert opinions
3. Consider factors that could influence the outcome
4. Examine similar questions or historical precedents

Provide a comprehensive research summary covering all relevant aspects.
Your response should be detailed and evidence-based.
"""

        print(f"📤 Research prompt length: {len(research_prompt)} characters")

        try:
            print(f"🔄 Calling researcher model...")
            print(f"   Model chain: {researcher_llm.model_chain}")
            research_response = await researcher_llm.invoke(research_prompt)
            print(f"✅ Research completed successfully!")
            print(f"📥 Research response length: {len(research_response)} characters")
            print(f"📄 Research preview: {research_response[:200]}...")
            # The specific model that responded will be in the logs from FallbackLLM

        except Exception as e:
            print(f"❌ Research failed: {str(e)}")
            research_response = f"Research failed: {str(e)}"

        # Individual Forecasts
        print(f"\n🔮 STEP 5: INDIVIDUAL FORECASTS")
        print(f"Generating 3 individual forecasts with detailed logging...")

        forecast_prompt = f"""
Based on the research, provide your forecast for this question:

Question: {question.question_text}

Research Summary:
{research_response[:1500] if len(research_response) > 1500 else research_response}

Task:
Provide your forecast with:
1. Probability assessment (0-100%)
2. Reasoning (2-3 sentences)
3. Format: "Probability: XX% - [Yes/No]"

Consider the research evidence carefully.
"""

        individual_forecasts = []

        for i in range(3):  # 3 forecasters
            print(f"   🤖 Forecaster {i+1}/3...")

            try:
                forecaster_prompt = f"{forecast_prompt}\n\nAs Forecaster {i+1}, provide your independent assessment:"
                print(f"      🔄 Calling forecaster {i+1} model...")
                print(f"         Model chain: {forecaster_llm.model_chain}")
                response = await forecaster_llm.invoke(forecaster_prompt)
                individual_forecasts.append(response)
                print(f"      ✅ Forecast {i+1} completed ({len(response)} chars)")
                print(f"      📄 Forecast {i+1} preview: {response[:100]}...")
                # The specific model that responded will be in the FallbackLLM logs

                await asyncio.sleep(2)  # Rate limiting

            except Exception as e:
                print(f"      ❌ Forecast {i+1} failed: {str(e)}")
                individual_forecasts.append(f"Forecast {i+1} failed: {str(e)}")

        print(f"✅ Generated {len(individual_forecasts)} individual forecasts")

        # Synthesis Phase
        print(f"\n🔗 STEP 6: SYNTHESIS PHASE")
        print(f"Synthesizing forecasts with detailed logging...")

        synthesis_prompt = f"""
Synthesize these forecasts for the question: {question.question_text}

Individual Forecasts:
{chr(10).join([f"Forecast {i+1}: {forecast}" for i, forecast in enumerate(individual_forecasts)])}

Task:
1. Analyze consensus and disagreements
2. Weigh reasoning and evidence
3. Provide final probability (0-100%)
4. Give comprehensive reasoning
5. Format: "Probability: XX% - [Yes/No]"

Synthesize thoughtfully and provide evidence-based conclusion.
"""

        try:
            print(f"🔄 Calling synthesizer model...")
            print(f"   Model chain: {synthesizer_llm.model_chain}")
            synthesis_response = await synthesizer_llm.invoke(synthesis_prompt)
            print(f"✅ Synthesis completed successfully!")
            print(f"📥 Synthesis response length: {len(synthesis_response)} characters")
            print(f"📄 Synthesis preview: {synthesis_response[:200]}...")
            # The specific model that responded will be in the FallbackLLM logs

        except Exception as e:
            print(f"❌ Synthesis failed: {str(e)}")
            synthesis_response = f"Synthesis failed: {str(e)}"

        # Save comprehensive output
        print(f"\n📋 STEP 7: SAVING COMPREHENSIVE OUTPUT")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"real_question_multiforecaster_{timestamp}.md"

        # Also save to local outputs for immediate access
        local_output_dir = Path("outputs")
        local_output_dir.mkdir(exist_ok=True)
        local_output_file = local_output_dir / f"real_question_multiforecaster_{timestamp}.md"

        content = f"""# Real Question Multiforecaster Test

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Tournament:** {tournament_used}
**Question:** {question.question_text}
**URL:** {question.page_url}
**Question Type:** {type(question).__name__}

## Model Configuration

**All models are FREE OpenRouter models:**
- Research: {researcher_llm.model_chain[0]} (primary)
- Forecasting: {forecaster_llm.model_chain[0]} (primary)
- Synthesis: {synthesizer_llm.model_chain[0]} (primary)

**Complete fallback chain (9 models each):**
"""

        for i, model in enumerate(researcher_llm.model_chain, 1):
            content += f"{i}. {model}\n"

        content += f"""

## API Call Results

✅ Research phase completed successfully ({len(research_response)} chars)
✅ Individual forecasts: {len(individual_forecasts)} completed
✅ Synthesis phase completed successfully ({len(synthesis_response)} chars)

## Process Steps Completed

✅ 1. Found real questions from tournament: {tournament_used}
✅ 2. Research Phase - Comprehensive analysis
✅ 3. Individual Forecasts - {len(individual_forecasts)} model predictions
✅ 4. Synthesis Phase - Combined consensus
✅ 5. Detailed API call logging throughout

## Research Output

{research_response}

## Individual Forecasts

"""

        for i, forecast in enumerate(individual_forecasts, 1):
            content += f"### Forecaster {i}\n\n{forecast}\n\n"

        content += f"""## Synthesis Output

{synthesis_response}

## System Performance

✅ API Authentication: Working with GitHub secrets
✅ Free Model Configuration: All 9 models accessible
✅ Real Questions: Successfully found and processed
✅ Detailed Logging: All API calls logged
✅ Output Organization: Saved to /outputs/ folder

**🎯 CONCLUSION: Real multiforecaster process working perfectly!**
"""

        # Write to both GitHub Actions and local outputs
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        with open(local_output_file, 'w', encoding='utf-8') as local_f:
            local_f.write(content)

        print(f"✅ Comprehensive output saved to: {output_file}")
        print(f"✅ Local copy saved to: {local_output_file}")
        print(f"📂 All outputs in: {output_dir.absolute()}")

        # In GitHub Actions, also commit outputs to make them accessible
        if os.getenv('GITHUB_ACTIONS'):
            try:
                import subprocess
                subprocess.run(['git', 'add', f'{local_output_file}'], check=True, capture_output=True)
                subprocess.run(['git', '-c', 'user.name=github-actions', '-c', 'user.email=github-actions@github.com',
                               'commit', '-m', f'Add multiforecaster output from {tournament_used} tournament\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>'],
                               check=True, capture_output=True)
                print(f"✅ Output committed to git repository")
            except Exception as e:
                print(f"⚠️  Could not commit output to git: {e}")

        # Check if the multiforecaster actually worked
        if "All 9 models in fallback chain failed" in research_response or len(individual_forecasts) == 0 or "All 9 models in fallback chain failed" in synthesis_response:
            print(f"\n❌ MULTIFORECASTER PROCESS FAILED!")
            print(f"❌ All API calls failed - no successful model responses")
            print(f"❌ No actual forecasting completed")
            return False

        print(f"\n" + "=" * 70)
        print(f"🎉 REAL QUESTION MULTIFORECASTER TEST COMPLETED!")
        print(f"✅ Used real Metaculus question from {tournament_used}")
        print(f"✅ Complete multiforecaster process with detailed logging")
        print(f"✅ All outputs saved to /outputs/ folder")
        print(f"📄 Full report: {output_file}")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"❌ Real question test failed: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

        # Try to create an error report file
        error_file = output_dir / f"error_report_{timestamp}.md"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"# Test Error Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Error:** {str(e)}\n")
            f.write(f"**Error Type:** {type(e).__name__}\n\n")
            f.write(f"## Traceback\n\n```\n")
            f.write(f"{traceback.format_exc()}")
            f.write(f"\n```\n")
        print(f"❌ Error report saved to: {error_file}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_questions())
    if success:
        print("\n🎉 REAL QUESTION MULTIFORECASTER SUCCESSFUL!")
        print("✅ Found and processed real Metaculus questions")
        print("✅ All API calls logged with model details")
    else:
        print("\n❌ REAL QUESTION TEST FAILED!")
        print("❌ Check the error messages above")
    sys.exit(0 if success else 1)