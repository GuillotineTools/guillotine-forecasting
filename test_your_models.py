import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Let's test the exact same models that work in your other instances
from forecasting_tools import GeneralLlm

async def test_working_models():
    print("Testing models that should work based on your experience...")
    
    # These are models you've said work fine in other instances
    test_models = [
        "moonshotai/kimi-k2-0905",  # Kimi
        "deepseek/deepseek-chat-v3-0324",  # DeepSeek
    ]
    
    # Also test with openrouter prefix
    test_models_with_prefix = [
        "openrouter/moonshotai/kimi-k2-0905",
        "openrouter/deepseek/deepseek-chat-v3-0324",
    ]
    
    test_prompt = "What is 2+2? Just give the answer as a number."
    
    print("Testing models without openrouter prefix:")
    for model in test_models:
        print(f"\nTesting model: {model}")
        try:
            llm = GeneralLlm(
                model=model,
                temperature=0.3,
                timeout=30,
                allowed_tries=1,
            )
            response = await llm.invoke(test_prompt)
            print(f"[RESULT] Model {model} response: {response.strip()}")
        except Exception as e:
            print(f"[ERROR] Model {model} failed: {e}")
    
    print("\n" + "="*50)
    print("Testing models with openrouter prefix:")
    for model in test_models_with_prefix:
        print(f"\nTesting model: {model}")
        try:
            llm = GeneralLlm(
                model=model,
                temperature=0.3,
                timeout=30,
                allowed_tries=1,
            )
            response = await llm.invoke(test_prompt)
            print(f"[RESULT] Model {model} response: {response.strip()}")
        except Exception as e:
            print(f"[ERROR] Model {model} failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_working_models())