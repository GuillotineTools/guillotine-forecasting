import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Test direct LiteLLM configuration
import litellm
from litellm import acompletion

async def test_litellm_direct():
    print("Testing LiteLLLLM direct configuration...")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("[FAIL] No API key found")
        return
    
    # Configure LiteLLM to use OpenRouter
    litellm.set_verbose = True  # Enable verbose logging
    
    # Set the API key for OpenRouter
    litellm.api_key = api_key
    
    # Test a working model first
    print("\nTesting a known working model:")
    try:
        response = await acompletion(
            model="openrouter/openai/gpt-4o-mini",
            messages=[{"role": "user", "content": "2+2="}],
            temperature=0.3,
            max_tokens=10
        )
        answer = response.choices[0].message.content.strip()
        print(f"[PASS] openrouter/openai/gpt-4o-mini: {answer}")
    except Exception as e:
        print(f"[FAIL] openrouter/openai/gpt-4o-mini: {e}")
    
    # Test the models you want to use
    test_models = [
        "openrouter/moonshotai/kimi-k2-0905",
        "openrouter/deepseek/deepseek-chat-v3-0324"
    ]
    
    print("\nTesting target models with LiteLLM direct:")
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
    asyncio.run(test_litellm_direct())