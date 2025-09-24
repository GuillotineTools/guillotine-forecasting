import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import GeneralLlm

async def test_forecaster_models():
    print("Testing specific forecaster models from main.py...")
    
    # These are the specific models used in the bot
    forecaster_models = {
        "forecaster1": "openrouter/moonshotai/kimi-k2-0905",
        "forecaster2": "openrouter/deepseek/deepseek-r1",
        "forecaster3": "openrouter/qwen/qwen3-max",
        "forecaster4": "openrouter/mistralai/mistral-large",
        "forecaster5": "openrouter/bytedance/seed-oss-36b-instruct",
        "forecaster6": "openrouter/microsoft/wizardlm-2-8x22b",
        "synthesizer": "openrouter/openai/gpt-4o",
        "parser": "openrouter/openai/gpt-4o-mini",
        "researcher": "openrouter/openai/gpt-4o-mini",
    }
    
    test_prompt = "What is 2+2?"
    
    for key, model in forecaster_models.items():
        print(f"\nTesting {key}: {model}")
        try:
            llm = GeneralLlm(
                model=model,
                temperature=0.3,
                timeout=30,
                allowed_tries=1,
            )
            response = await llm.invoke(test_prompt)
            print(f"[PASS] {key} ({model}) works! Response: {response[:50]}...")
        except Exception as e:
            print(f"[FAIL] {key} ({model}) failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_forecaster_models())