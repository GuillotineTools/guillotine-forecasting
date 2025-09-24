import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import GeneralLlm

async def test_exact_forecaster_models():
    print("Testing the exact forecaster models from the original bot...")
    
    # These are the exact model names from the original bot that were failing
    forecaster_models = [
        "openrouter/moonshotai/kimi-k2-0905",
        "openrouter/deepseek/deepseek-r1",
        "openrouter/qwen/qwen3-max",
        "openrouter/mistralai/mistral-large",
        "openrouter/bytedance/seed-oss-36b-instruct",
        "openrouter/microsoft/wizardlm-2-8x22b",
    ]
    
    test_prompt = "What is 2+2?"
    
    for model in forecaster_models:
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
    asyncio.run(test_exact_forecaster_models())