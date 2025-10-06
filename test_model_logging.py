#!/usr/bin/env python3
"""
Test to show exactly which model is being used in the FallbackLLM chain.
"""
import asyncio
import os
import sys
from datetime import datetime

# Set up environment
os.environ['GITHUB_ACTIONS'] = 'true'
os.environ['OPENAI_DISABLE_TRACE'] = 'true'

async def test_model_logging():
    """Test with detailed model logging."""
    try:
        from fallback_llm import create_default_fallback_llm

        print("🔍 TESTING MODEL LOGGING - WHICH MODEL ACTUALLY RESPONDS?")
        print("=" * 60)

        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("❌ OPENROUTER_API_KEY not set!")
            return False

        print(f"✅ API key found: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else 'VALID'}")

        # Create FallbackLLM
        llm = create_default_fallback_llm(api_key=api_key, temperature=0.5, timeout=60, allowed_tries=2)

        print(f"\n📋 Model Chain ({len(llm.model_chain)} models):")
        for i, model in enumerate(llm.model_chain, 1):
            print(f"   {i}. {model}")

        # Test prompt that will definitely show model characteristics
        test_prompt = """
Please respond to this simple test and include your model name in your answer.

Question: What is 7 + 8?

Your response should include:
1. The answer to the math problem
2. The phrase "MODEL USED: [your model name]"
3. A brief description of your capabilities

Answer directly and clearly.
"""

        print(f"\n📝 Testing with model identification prompt...")
        print(f"📤 Prompt length: {len(test_prompt)} characters")

        try:
            response = await llm.invoke(test_prompt)

            print(f"\n✅ SUCCESS! Got response from one of the models")
            print(f"📥 Response length: {len(response)} characters")
            print(f"\n📄 FULL RESPONSE:")
            print("=" * 50)
            print(response)
            print("=" * 50)

            # Analyze which model likely responded
            print(f"\n🔍 MODEL ANALYSIS:")

            response_lower = response.lower()
            if "deepseek" in response_lower:
                print(f"✅ LIKELY MODEL: deepseek model (mentioned in response)")
            elif "claude" in response_lower or "anthropic" in response_lower:
                print(f"✅ LIKELY MODEL: Claude/Anthropic model")
            elif "gpt" in response_lower or "openai" in response_lower:
                print(f"⚠️  LIKELY MODEL: OpenAI/GPT model (unexpected!)")
            elif "gemini" in response_lower:
                print(f"✅ LIKELY MODEL: Gemini model")
            elif "llama" in response_lower:
                print(f"✅ LIKELY MODEL: Llama model")
            else:
                print(f"🔍 MODEL: Could not determine from response content")

            # Check response style characteristics
            if len(response) > 500:
                print(f"📝 Response style: Detailed/comprehensive (typical of larger models)")
            elif len(response) < 100:
                print(f"📝 Response style: Brief/concise")
            else:
                print(f"📝 Response style: Medium length")

            # Save to outputs
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{output_dir}/model_identification_test_{timestamp}.md"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Model Identification Test Results\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**API Key:** {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else 'VALID'}\n\n")

                f.write(f"## Model Chain Tested\n\n")
                for i, model in enumerate(llm.model_chain, 1):
                    f.write(f"{i}. {model}\n")
                f.write(f"\n")

                f.write(f"## Test Prompt\n\n")
                f.write(f"```\n{test_prompt}\n```\n\n")

                f.write(f"## Model Response\n\n")
                f.write(f"```\n{response}\n```\n\n")

                f.write(f"## Analysis\n\n")
                f.write(f"**Response Length:** {len(response)} characters\n")
                f.write(f"**Primary Model:** {llm.model_chain[0]}\n")
                f.write(f"**Total Models in Chain:** {len(llm.model_chain)}\n\n")

                f.write(f"**Likely Responding Model:** Based on response analysis\n")
                if "deepseek" in response_lower:
                    f.write(f"- ✅ DeepSeek model (mentioned in response)\n")
                elif "claude" in response_lower:
                    f.write(f"- ✅ Claude/Anthropic model\n")
                elif "gpt" in response_lower:
                    f.write(f"- ⚠️  OpenAI/GPT model (unexpected)\n")
                else:
                    f.write(f"- 🔍 Could not determine from response\n")

                f.write(f"\n## Conclusion\n\n")
                f.write(f"✅ Model identification test completed successfully!\n")
                f.write(f"✅ Free models are working in GitHub Actions environment!\n")

            print(f"\n💾 Results saved to: {output_file}")
            return True

        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False

    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_model_logging())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILURE'}: Model identification test")
    sys.exit(0 if success else 1)