import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import GeneralLlm

async def test_specific_models():
    print("Testing specific models that were failing...")
    
    # These are the specific models that were failing
    specific_models = [
        "openrouter/moonshotai/kimi-k2-0905",
        "openrouter/deepseek/deepseek-chat-v3-0324",
        "moonshotai/kimi-k2-0905",  # Try without openrouter prefix
        "deepseek/deepseek-chat-v3-0324",  # Try without openrouter prefix
    ]
    
    test_prompt = "Say 'Hello, World!'"
    
    for model in specific_models:
        print(f"\nTesting model: {model}")
        try:
            llm = GeneralLlm(
                model=model,
                temperature=0.3,
                timeout=30,
                allowed_tries=1,
            )
            response = await llm.invoke(test_prompt)
            print(f"[PASS] Model {model} works! Response: {response[:50]}...")
        except Exception as e:
            print(f"[FAIL] Model {model} failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_specific_models())