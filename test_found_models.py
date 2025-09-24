import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from forecasting_tools import GeneralLlm

async def test_found_models():
    print("Testing models that were found in the API...")
    
    # These are models that were found in the API
    found_models = [
        "moonshotai/kimi-k2-0905",
        "deepseek/deepseek-chat", 
        "deepseek/deepseek-chat-v3-0324",
        "qwen/qwen3-max",
        "mistralai/mistral-large",
        "bytedance/seed-oss-36b-instruct",
        "microsoft/wizardlm-2-8x22b"
    ]
    
    test_prompt = "What is 2+2? Just give the number."
    
    for model in found_models:
        print(f"\nTesting model: {model}")
        try:
            llm = GeneralLlm(
                model=model,
                temperature=0.3,
                timeout=30,
                allowed_tries=1,
            )
            response = await llm.invoke(test_prompt)
            print(f"[PASS] Model {model} works! Response: {response.strip()}")
        except Exception as e:
            print(f"[FAIL] Model {model} failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_found_models())