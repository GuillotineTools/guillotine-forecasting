#!/usr/bin/env python3
"""
Test the current free model configuration with actual API calls.
This will verify that the new configuration works properly.
"""
import asyncio
import os
import sys
from datetime import datetime

# Set up environment to simulate GitHub Actions
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

async def test_current_free_models():
    """Test the current free model configuration."""
    try:
        from fallback_llm import create_default_fallback_llm, create_research_fallback_llm, create_synthesis_fallback_llm

        print("🤖 TESTING CURRENT FREE MODEL CONFIGURATION")
        print("=" * 60)
        print("This will test the exact configuration that GitHub Actions will use")

        # Get API key
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY is not set!")
            print("💡 In GitHub Actions, this comes from secrets.OPENROUTER_API_KEY")
            return False

        print(f"✅ API key found: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else 'VALID'}")

        # Test the exact same configuration as main.py
        print("\n🔧 Testing FallbackLLM with current free model chain...")

        default_llm = create_default_fallback_llm(
            api_key=api_key,
            temperature=0.5,
            timeout=60,
            allowed_tries=2
        )

        print(f"✅ FallbackLLM created with model chain:")
        for i, model in enumerate(default_llm.model_chain, 1):
            print(f"   {i}. {model}")

        # Test with a simple forecast-style prompt
        test_prompt = """
Question: Will artificial general intelligence (AGI) be achieved before 2030?

Provide a brief forecast with your probability assessment and reasoning.

Your response should include:
1. Your probability assessment (0-100%)
2. Brief reasoning (2-3 sentences)
3. Final answer format: "Probability: XX% - [Yes/No]"
"""

        print(f"\n📝 Testing with forecast prompt ({len(test_prompt)} characters)...")

        try:
            response = await default_llm.invoke(test_prompt)

            print(f"✅ SUCCESS! Free model configuration works!")
            print(f"📥 Response length: {len(response)} characters")
            print(f"📄 Response preview:")
            print("=" * 40)
            print(response[:500])
            if len(response) > 500:
                print("...")
            print("=" * 40)

            # Save test result
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)

            test_file = f"{output_dir}/free_models_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"# Free Model Configuration Test\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Status:** SUCCESS ✅\n")
                f.write(f"**API Key:** {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else 'VALID'}\n")
                f.write(f"**Models Tested:** {len(default_llm.model_chain)} free models\n\n")
                f.write(f"## Model Chain\n\n")
                for i, model in enumerate(default_llm.model_chain, 1):
                    f.write(f"{i}. {model}\n")
                f.write(f"\n## Test Prompt\n\n")
                f.write(f"```\n{test_prompt}\n```\n\n")
                f.write(f"## Model Response\n\n")
                f.write(f"```\n{response}\n```\n\n")
                f.write(f"## Conclusion\n\n")
                f.write(f"✅ Free model configuration is working properly!\n")
                f.write(f"✅ GitHub Actions should work with this setup!\n")

            print(f"\n💾 Test result saved to: {test_file}")
            return True

        except Exception as e:
            print(f"❌ FAILED: Free model configuration error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return False

    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_current_free_models())
    if success:
        print("\n🎉 FREE MODEL CONFIGURATION WORKS!")
        print("✅ GitHub Actions should work with the new free model setup")
    else:
        print("\n❌ FREE MODEL CONFIGURATION FAILED!")
        print("❌ GitHub Actions will likely fail with current setup")
    sys.exit(0 if success else 1)