import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import GeneralLlm

async def test_openrouter_api():
    print("Testing OpenRouter API key and model availability...")
    
    # Check if API key is loaded
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        return
    
    print(f"[PASS] OPENROUTER_API_KEY is set (length: {len(api_key)} characters)")
    
    # Test with the exact model from main.py that's failing
    test_models = [
        "openrouter/openai/gpt-4o-mini",
        "openrouter/openai/gpt-4o",
        "gpt-4o-mini",  # Direct OpenAI model
        "gpt-4o"        # Direct OpenAI model
    ]
    
    test_prompt = "Say 'Hello, World!'"
    
    for model in test_models:
        print(f"\nTesting model: {model}")
        try:
            llm = GeneralLlm(
                model=model,
                temperature=0.3,
                timeout=30,
                allowed_tries=1,  # Reduce retries for faster testing
            )
            response = await llm.invoke(test_prompt)
            print(f"[PASS] Model {model} works! Response: {response}")
        except Exception as e:
            print(f"[FAIL] Model {model} failed: {e}")
            # Check if it's a model availability issue
            if "No allowed providers are available" in str(e):
                print(f"   This model may not be available with your API key")

if __name__ == "__main__":
    asyncio.run(test_openrouter_api())