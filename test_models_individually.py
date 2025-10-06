#!/usr/bin/env python3
"""
Test each OpenRouter model individually to find working ones.
"""
import asyncio
import os
import sys
import logging
from datetime import datetime

# Set up environment
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

# Test models - add or modify the ones you want to test
TEST_MODELS = [
    "openrouter/deepseek/deepseek-r1:free",
    "openrouter/openai/gpt-4o-mini",
    "openrouter/x-ai/grok-4-fast:free",
    "openrouter/meta-llama/llama-3.1-8b-instruct:free",
    "openrouter/microsoft/phi-3-medium-128k-instruct:free",
    "openrouter/mistralai/mistral-7b-instruct:free",
    "openrouter/google/gemma-2-9b-it:free",
    "openrouter/perplexity/sonar",
    # Add any other models you want to test
]

async def test_model(model_name, api_key):
    """Test a single model with a simple request."""
    try:
        from fallback_llm import FallbackLLM

        print(f"\n🔄 Testing model: {model_name}")
        print(f"   API key: {'✓ SET' if api_key else '❌ NOT SET'}")

        if not api_key:
            print(f"❌ {model_name}: FAILED - No API key")
            return False

        # Create a single-model FallbackLLM
        test_llm = FallbackLLM(
            model_chain=[model_name],
            api_key=api_key,
            allowed_tries=1,
            timeout=30
        )

        # Simple test prompt
        test_prompt = "What is 2+2? Answer with just the number."
        print(f"   Prompt: '{test_prompt}'")

        response = await test_llm.invoke(test_prompt)

        print(f"✅ {model_name}: SUCCESS")
        print(f"   Response: {response}")
        return True

    except Exception as e:
        print(f"❌ {model_name}: FAILED - {str(e)}")
        return False

async def main():
    """Test all models and create a working fallback chain."""
    print("🤖 TESTING OPENROUTER MODELS INDIVIDUALLY")
    print("=" * 60)

    # Get API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY is not set!")
        print("Please set it and run again.")
        return False

    print(f"✅ API key found: {api_key[:10]}..." if len(api_key) > 10 else f"✅ API key found")

    working_models = []
    failed_models = []

    print(f"\n📋 Testing {len(TEST_MODELS)} models...")

    for i, model in enumerate(TEST_MODELS, 1):
        print(f"\n[{i}/{len(TEST_MODELS)}] Testing {model}")
        success = await test_model(model, api_key)

        if success:
            working_models.append(model)
        else:
            failed_models.append(model)

    print(f"\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)

    print(f"✅ Working models ({len(working_models)}):")
    for model in working_models:
        print(f"   - {model}")

    print(f"\n❌ Failed models ({len(failed_models)}):")
    for model in failed_models:
        print(f"   - {model}")

    if len(working_models) == 0:
        print("\n❌ No working models found! Check your API key and try different models.")
        return False

    print(f"\n💡 RECOMMENDATION: Update fallback_llm.py to use these working models:")
    print("model_chain = [")
    for model in working_models:
        print(f'        "{model}",')
    print("    ]")

    # Save working models to a file
    with open('working_models.txt', 'w') as f:
        f.write("# Working OpenRouter models from individual tests\n")
        f.write(f"# Generated on {datetime.now()}\n\n")
        f.write("working_models = [\n")
        for model in working_models:
            f.write(f'    "{model}",\n')
        f.write("]\n")

    print(f"\n💾 Working models saved to 'working_models.txt'")

    return len(working_models) > 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)