#!/usr/bin/env python3
"""
Test DeepSeek models with actual prompts to see exact API responses.
"""
import asyncio
import os
import sys
from datetime import datetime

# Set up environment to simulate GitHub Actions
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

# Working DeepSeek models from our test
DEEPSEEK_MODELS = [
    "openrouter/deepseek/deepseek-chat",
    "openrouter/deepseek/deepseek-chat-v3",
]

# Test prompts that mimic what the bot actually uses
TEST_PROMPTS = [
    {
        "name": "Simple Math Test",
        "prompt": "What is 2+2? Answer with just the number.",
        "expected": "4"
    },
    {
        "name": "Research Question Test",
        "prompt": "Research this question: Will the age of the oldest human as of 2100 exceed 125 years? Provide a brief analysis of current records and trends.",
        "expected": "analysis of longevity trends"
    },
    {
        "name": "Forecast Test",
        "prompt": "Based on current longevity records and medical advancements, what is the probability (0-100%) that someone will live to be 130 years old by 2100? Just give the number.",
        "expected": "probability percentage"
    }
]

async def test_model_with_prompt(model_name, prompt_data, api_key):
    """Test a single model with a specific prompt and show exact response."""
    try:
        from fallback_llm import FallbackLLM

        print(f"\n{'='*80}")
        print(f"🔄 TESTING: {model_name}")
        print(f"📝 PROMPT TYPE: {prompt_data['name']}")
        print(f"📤 EXACT PROMPT SENT:")
        print(f"'{prompt_data['prompt']}'")
        print(f"{'='*80}")

        # Create a single-model FallbackLLM
        test_llm = FallbackLLM(
            model_chain=[model_name],
            api_key=api_key,
            allowed_tries=1,
            timeout=30
        )

        # Make the API call
        print(f"⏳ Making API call...")
        response = await test_llm.invoke(prompt_data['prompt'])

        print(f"✅ API CALL SUCCESSFUL")
        print(f"📥 RAW RESPONSE FROM MODEL:")
        print(f"---BEGIN MODEL RESPONSE---")
        print(repr(response))
        print(f"---END MODEL RESPONSE---")
        print(f"\n📥 FORMATTED RESPONSE:")
        print(response)
        print(f"{'='*80}")

        return response

    except Exception as e:
        print(f"❌ API CALL FAILED")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"{'='*80}")
        return None

async def main():
    """Test all DeepSeek models with different prompts."""
    print("🤖 TESTING DEEPSEEK MODELS - EXACT API RESPONSES")
    print("=" * 100)
    print("This will show the EXACT output from each model API call")
    print("=" * 100)

    # Get API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY is not set!")
        return False

    print(f"✅ Using API key: {api_key[:10]}...{api_key[-4:]}")

    results = {}

    for model in DEEPSEEK_MODELS:
        print(f"\n🔸 TESTING MODEL: {model}")
        results[model] = {}

        for prompt_data in TEST_PROMPTS:
            response = await test_model_with_prompt(model, prompt_data, api_key)
            results[model][prompt_data['name']] = response

            # Small delay between calls
            await asyncio.sleep(2)

    # Summary
    print(f"\n" + "=" * 100)
    print("📊 SUMMARY OF ALL API RESPONSES")
    print("=" * 100)

    for model in DEEPSEEK_MODELS:
        print(f"\n🤖 {model}:")
        for prompt_name, response in results[model].items():
            status = "✅ SUCCESS" if response else "❌ FAILED"
            print(f"   {prompt_name}: {status}")
            if response:
                print(f"      Response: {repr(response[:100])}{'...' if len(response) > 100 else ''}")

    # Save detailed results
    with open('deepseek_api_responses.txt', 'w') as f:
        f.write("# DeepSeek Model API Responses\n")
        f.write(f"# Generated on {datetime.now()}\n\n")

        for model in DEEPSEEK_MODELS:
            f.write(f"## {model}\n\n")
            for prompt_name, response in results[model].items():
                f.write(f"### {prompt_name}\n")
                f.write(f"Prompt: {prompt_data['prompt']}\n")
                if response:
                    f.write(f"Response: {repr(response)}\n")
                else:
                    f.write("Response: FAILED\n")
                f.write("\n")
            f.write("\n")

    print(f"\n💾 Detailed responses saved to 'deepseek_api_responses.txt'")

    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)