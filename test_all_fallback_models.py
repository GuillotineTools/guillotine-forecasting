#!/usr/bin/env python3
"""
Test all models in the fallback chain and save outputs to markdown files.
"""
import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Set up environment to simulate GitHub Actions
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

# Your specified fallback models
SPECIFIED_MODELS = [
    "openrouter/deepseek/deepseek-chat",
    "openrouter/deepseek/deepseek-chat-v3",
    "openrouter/tngtech/deepseek-r1t2-chimera:free",
    "openrouter/z-ai/glm-4.5-air:free",
    "openrouter/tngtech/deepseek-r1t-chimera:free",
    "openrouter/microsoft/mai-ds-r1:free",
    "openrouter/qwen/qwen3-235b-a22b:free",
    "openrouter/google/gemini-2.0-flash-exp:free",
    "openrouter/meta-llama/llama-3.3-70b-instruct:free"
]

# Additional free models to try if specified ones fail
BACKUP_FREE_MODELS = [
    "openrouter/deepseek/deepseek-r1:free",
    "openrouter/meta-llama/llama-3.1-8b-instruct:free",
    "openrouter/microsoft/phi-3-medium-128k-instruct:free",
    "openrouter/mistralai/mistral-7b-instruct:free",
    "openrouter/mistralai/mistral-nemo:free",
    "openrouter/google/gemma-2-9b-it:free",
    "openrouter/x-ai/grok-4-fast:free",
    "openrouter/openai/gpt-4o-mini",
    "openrouter/perplexity/sonar"
]

# Test prompts
TEST_PROMPTS = [
    {
        "name": "Simple Math",
        "prompt": "What is 2+2? Answer with just the number.",
        "expected_type": "number"
    },
    {
        "name": "Research Analysis",
        "prompt": "Research this question: Will artificial general intelligence (AGI) be developed before 2030? Provide a brief analysis of current AI capabilities and expert opinions.",
        "expected_type": "analysis"
    },
    {
        "name": "Forecast Probability",
        "prompt": "Based on current AI development trends, what is the probability (0-100%) that AGI will be developed before 2030? Just give the number.",
        "expected_type": "percentage"
    },
    {
        "name": "Complex Reasoning",
        "prompt": "If a train travels 300 miles in 4 hours, and another train travels 450 miles in 6 hours, which train is faster and what is the speed difference?",
        "expected_type": "reasoning"
    }
]

async def test_model_with_prompts(model_name, api_key, output_dir):
    """Test a single model with all prompts and save results."""
    print(f"\n{'='*80}")
    print(f"🔄 TESTING MODEL: {model_name}")
    print(f"{'='*80}")

    results = {
        "model": model_name,
        "test_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S JST'),
        "prompts": {}
    }

    try:
        from fallback_llm import FallbackLLM

        # Create a single-model FallbackLLM
        test_llm = FallbackLLM(
            model_chain=[model_name],
            api_key=api_key,
            allowed_tries=1,
            timeout=60
        )

        for prompt_data in TEST_PROMPTS:
            print(f"\n📝 Testing: {prompt_data['name']}")
            print(f"📤 Prompt: '{prompt_data['prompt']}'")

            try:
                # Make the API call
                response = await test_llm.invoke(prompt_data['prompt'])

                print(f"✅ SUCCESS")
                print(f"📥 Response: {response}")

                results["prompts"][prompt_data['name']] = {
                    "prompt": prompt_data['prompt'],
                    "response": response,
                    "success": True,
                    "error": None
                }

            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                results["prompts"][prompt_data['name']] = {
                    "prompt": prompt_data['prompt'],
                    "response": None,
                    "success": False,
                    "error": str(e)
                }

            # Small delay between calls
            await asyncio.sleep(2)

        # Determine if model is working (at least 2/4 prompts successful)
        successful_prompts = sum(1 for p in results["prompts"].values() if p["success"])
        model_working = successful_prompts >= 2

        results["overall_status"] = "WORKING" if model_working else "FAILED"
        results["success_rate"] = f"{successful_prompts}/{len(TEST_PROMPTS)}"

        print(f"\n📊 Model Status: {results['overall_status']}")
        print(f"📊 Success Rate: {results['success_rate']}")

        # Save results to markdown file
        await save_model_results_to_markdown(results, output_dir)

        return model_working, results

    except Exception as e:
        print(f"❌ MODEL INITIALIZATION FAILED: {str(e)}")
        results["overall_status"] = "INITIALIZATION_FAILED"
        results["error"] = str(e)

        # Save failed results
        await save_model_results_to_markdown(results, output_dir)

        return False, results

async def save_model_results_to_markdown(results, output_dir):
    """Save model test results to a markdown file."""
    model_name = results["model"].replace("/", "_").replace(":", "_")
    filename = f"model_test_{model_name}.md"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Model Test Results: {results['model']}\n\n")
        f.write(f"**Test Timestamp:** {results['test_timestamp']}\n")
        f.write(f"**Overall Status:** {results['overall_status']}\n")

        if 'success_rate' in results:
            f.write(f"**Success Rate:** {results['success_rate']}\n")

        if 'error' in results:
            f.write(f"**Initialization Error:** {results['error']}\n")

        f.write(f"\n---\n\n")

        for prompt_name, prompt_result in results["prompts"].items():
            f.write(f"## {prompt_name} Test\n\n")
            f.write(f"**Prompt:** `{prompt_result['prompt']}`\n\n")

            if prompt_result['success']:
                f.write(f"**Status:** ✅ SUCCESS\n\n")
                f.write(f"**Response:**\n```\n{prompt_result['response']}\n```\n\n")
            else:
                f.write(f"**Status:** ❌ FAILED\n\n")
                f.write(f"**Error:** {prompt_result['error']}\n\n")

            f.write("---\n\n")

async def fetch_openrouter_free_models(api_key):
    """Try to fetch additional free models from OpenRouter."""
    print(f"\n🔍 FETCHING ADDITIONAL FREE MODELS FROM OPENROUTER")

    # Common free models that we haven't tried yet
    additional_models = [
        "openrouter/meta-llama/llama-3.2-3b-instruct:free",
        "openrouter/microsoft/phi-3-mini-128k-instruct:free",
        "openrouter/mistralai/mistral-7b-instruct:free",
        "openrouter/google/gemma-2-2b-it:free",
        "openrouter/huggingfaceh4/zephyr-7b-beta:free",
        "openrouter/anthropic/claude-3-haiku",
        "openrouter/microsoft/wizardlm-2-8x22b",
        "openrouter/cognitivecomputations/dolphin-2.9.1-llama3-8b:free"
    ]

    return additional_models

async def main():
    """Test all models in the fallback chain."""
    print("🤖 TESTING ALL FALLBACK MODELS")
    print("=" * 100)

    # Get API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY is not set!")
        return False

    print(f"✅ Using API key: {api_key[:10]}...{api_key[-4:]}")

    # Create output directory
    output_dir = Path("model_test_results")
    output_dir.mkdir(exist_ok=True)

    all_results = {}
    working_models = []
    failed_models = []

    # Test specified models first
    print(f"\n🔸 TESTING SPECIFIED MODELS ({len(SPECIFIED_MODELS)} models)")

    for model in SPECIFIED_MODELS:
        is_working, results = await test_model_with_prompts(model, api_key, output_dir)
        all_results[model] = results

        if is_working:
            working_models.append(model)
        else:
            failed_models.append(model)

        # Delay between models
        await asyncio.sleep(3)

    # If too many failures, test backup models
    if len(failed_models) > len(SPECIFIED_MODELS) // 2:
        print(f"\n⚠️  MANY MODELS FAILED, TESTING BACKUP MODELS")

        backup_models = await fetch_openrouter_free_models(api_key)
        print(f"\n🔸 TESTING BACKUP MODELS ({len(backup_models)} models)")

        for model in backup_models:
            is_working, results = await test_model_with_prompts(model, api_key, output_dir)
            all_results[model] = results

            if is_working:
                working_models.append(model)

            # Delay between models
            await asyncio.sleep(3)

    # Save summary
    await save_summary_report(all_results, working_models, failed_models, output_dir)

    print(f"\n" + "=" * 100)
    print("📊 FINAL SUMMARY")
    print("=" * 100)
    print(f"✅ Working models ({len(working_models)}):")
    for model in working_models:
        print(f"   - {model}")

    print(f"\n❌ Failed models ({len(failed_models)}):")
    for model in failed_models:
        print(f"   - {model}")

    print(f"\n💾 Detailed results saved to: {output_dir}/")
    print(f"💾 Summary report saved to: {output_dir}/model_test_summary.md")

    return len(working_models) > 0

async def save_summary_report(all_results, working_models, failed_models, output_dir):
    """Save a comprehensive summary report."""
    filepath = output_dir / "model_test_summary.md"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# Fallback Model Test Summary\n\n")
        f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S JST')}\n")
        f.write(f"**Total Models Tested:** {len(all_results)}\n")
        f.write(f"**Working Models:** {len(working_models)}\n")
        f.write(f"**Failed Models:** {len(failed_models)}\n\n")

        f.write("## Working Models ✅\n\n")
        for model in working_models:
            f.write(f"- **{model}**\n")

        f.write("\n## Failed Models ❌\n\n")
        for model in failed_models:
            f.write(f"- **{model}**\n")

        f.write("\n## Detailed Results\n\n")
        for model, results in all_results.items():
            status = results["overall_status"]
            success_rate = results.get("success_rate", "N/A")

            f.write(f"### {model}\n")
            f.write(f"- **Status:** {status}\n")
            f.write(f"- **Success Rate:** {success_rate}\n")

            if "error" in results:
                f.write(f"- **Error:** {results['error']}\n")

            f.write("\n")

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)