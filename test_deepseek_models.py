#!/usr/bin/env python3
"""
Test DeepSeek models with GitHub repo secret OpenRouter API key.
"""
import asyncio
import os
import sys
from datetime import datetime

# Set up environment to simulate GitHub Actions
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

# DeepSeek models to test
DEEPSEEK_MODELS = [
    "openrouter/deepseek/deepseek-r1:free",
    "openrouter/deepseek/deepseek-chat",
    "openrouter/deepseek/deepseek-coder",
    "openrouter/deepseek/deepseek-chat-v3",
    # Add any other DeepSeek models you want to test
]

async def test_model(model_name, api_key):
    """Test a single DeepSeek model."""
    try:
        from fallback_llm import FallbackLLM

        print(f"\n🔄 Testing DeepSeek model: {model_name}")
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
    """Test all DeepSeek models."""
    print("🤖 TESTING DEEPSEEK MODELS WITH GITHUB SECRET")
    print("=" * 60)

    # Get API key from environment (should be set from GitHub secret)
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY is not set!")
        print("In GitHub Actions, this should be set from secrets.OPENROUTER_API_KEY")
        print("For local testing, set it manually:")
        print("export OPENROUTER_API_KEY=your_key_here")
        return False

    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else f"✅ API key found")

    working_models = []
    failed_models = []

    print(f"\n📋 Testing {len(DEEPSEEK_MODELS)} DeepSeek models...")

    for i, model in enumerate(DEEPSEEK_MODELS, 1):
        print(f"\n[{i}/{len(DEEPSEEK_MODELS)}] Testing {model}")
        success = await test_model(model, api_key)

        if success:
            working_models.append(model)
        else:
            failed_models.append(model)

    print(f"\n" + "=" * 60)
    print("📊 DEEPSEEK TEST RESULTS")
    print("=" * 60)

    print(f"✅ Working DeepSeek models ({len(working_models)}):")
    for model in working_models:
        print(f"   - {model}")

    print(f"\n❌ Failed DeepSeek models ({len(failed_models)}):")
    for model in failed_models:
        print(f"   - {model}")

    if len(working_models) == 0:
        print("\n❌ No DeepSeek models are working!")
        return False

    print(f"\n💡 These DeepSeek models can be used in the fallback chain:")
    for model in working_models:
        print(f"   - {model}")

    # Save working DeepSeek models to a file
    with open('working_deepseek_models.txt', 'w') as f:
        f.write("# Working DeepSeek OpenRouter models\n")
        f.write(f"# Generated on {datetime.now()}\n\n")
        f.write("working_deepseek_models = [\n")
        for model in working_models:
            f.write(f'    "{model}",\n')
        f.write("]\n")

    print(f"\n💾 Working DeepSeek models saved to 'working_deepseek_models.txt'")

    return len(working_models) > 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)