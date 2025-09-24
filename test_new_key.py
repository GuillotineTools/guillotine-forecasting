import os
import asyncio
from dotenv import load_dotenv

# Don't load the .env file since we want to test with your new key
# load_dotenv()

import litellm
from litellm import acompletion

async def test_new_api_key():
    print("Testing with your new API key...")
    
    # Use the new API key you provided
    new_api_key = "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"
    
    print(f"API Key prefix: {new_api_key[:15]}...")
    
    # Configure LiteLLM to use the new OpenRouter key
    litellm.api_key = new_api_key
    
    # Test the models you want to use
    test_models = [
        "openrouter/moonshotai/kimi-k2-0905",
        "openrouter/deepseek/deepseek-chat-v3-0324",
        "openrouter/openai/gpt-4o-mini"  # Test a working one for comparison
    ]
    
    print("\nTesting models with your new API key:")
    for model in test_models:
        try:
            response = await acompletion(
                model=model,
                messages=[{"role": "user", "content": "2+2="}],
                temperature=0.3,
                max_tokens=10
            )
            answer = response.choices[0].message.content.strip()
            print(f"[RESULT] {model}: {answer}")
        except Exception as e:
            print(f"[ERROR] {model}: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_api_key())